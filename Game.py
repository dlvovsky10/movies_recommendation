from Handlers import CLIIOHandler, BaseIOHandler
from user_movies_table import User_movie_table
from users import User, Authentication
import constants


class Game:
    def __init__(self, handler: BaseIOHandler):
        self.users = []
        self.signed_up_user = None
        self.is_on = True
        self.commands = {}
        self.handler = handler

    def set_commands(self):
        # This function now correctly assumes self.signed_up_user is not None
        self.commands = {
            1: self.signed_up_user.movies_table.add_movies_from_user,
            2: self.signed_up_user.movies_table.print_basic_stats,
            3: self.signed_up_user.movies_table.get_movie_recommendation,
            4: self.handle_users_comparison,
            5: self.handle_loading_from_json,
            6: self.signed_up_user.movies_table.to_json,
            7: lambda: self.signed_up_user.change_password(self.handler),  # Use lambda to pass handler
            8: self.logout_user
        }

    def logout_user(self):
        self.handler.display_output(f"Logging out {self.signed_up_user.user_name}...")
        self.signed_up_user = None
        self.commands = {}  # Clear user-specific commands

    def _is_username_taken(self, username: str) -> bool:
        return any(user.user_name == username for user in self.users)

    def show_main_menu(self):
        while self.is_on:
            if self.signed_up_user:
                self._show_user_menu()
                continue  # After logout, loop back to show main menu

            command = self.handler.get_user_input(constants.MAIN_MENU_MESSAGE + "\n")
            if command == '1':  # Login
                self._handle_log_in()
            elif command == '2':  # Signup
                self._handle_sign_up()
            elif command == '3':  # Exit
                self.is_on = False
            else:
                self.handler.display_output("Invalid command, please try again.")
        self.handler.display_output("Goodbye!")

    def _handle_sign_up(self):
        username = self.handler.get_user_input("Please enter you user name: ")
        if self._is_username_taken(username):
            self.handler.display_output("This username is already taken. Please try another one.")
            return

        new_user = User(user_name=username, user_id=len(self.users), handler=self.handler)
        self.users.append(new_user)
        self.signed_up_user = new_user
        self.handler.display_output(f"Welcome {username}! Signup successful.")
        self.set_commands()

    def _show_user_menu(self):
        self.handler.display_output("\n--- User Menu ---")
        command_str = self.handler.get_user_input(constants.USER_MENU_MESSAGE + "\n")

        if not command_str.isdigit() or int(command_str) not in self.commands:
            self.handler.display_output("Invalid command, please try again.")
            return

        command = int(command_str)

        action = self.commands.get(command)
        if action:
            action()

    def handle_users_comparison(self) -> None:
        another_user_name = self.handler.get_user_input("Enter another user name to compare with: ")

        if another_user_name == self.signed_up_user.user_name:
            self.handler.display_output("You can't compare a user with themselves.")
            return

        another_user = next((user for user in self.users if user.user_name == another_user_name), None)

        if not another_user:
            self.handler.display_output("User doesn't exist.")
            return

        are_similar = User_movie_table.are_similar(self.signed_up_user.movies_table, another_user.movies_table)

        if are_similar:
            self.handler.display_output(f"The taste of {self.signed_up_user.user_name} and the taste of "
                                        f"{another_user_name} are similar!")
            User_movie_table.movies_recommendations_based_on_similarity(
                self.signed_up_user.movies_table, another_user.movies_table, self.handler
            )
        else:
            self.handler.display_output(f"The taste of {self.signed_up_user.user_name} and the taste of "
                                        f"{another_user_name} are not similar.")

    def handle_loading_from_json(self):
        json_path = f"user_{self.signed_up_user.id}_data.json"
        new_table = User_movie_table.create_from_json(json_path, self.handler)
        if new_table:
            self.signed_up_user.movies_table = new_table
            self.handler.display_output("Movie data loaded successfully.")

    def _handle_log_in(self) -> None:
        user_name = self.handler.get_user_input("Enter user name: ")
        user_to_login = next((user for user in self.users if user.user_name == user_name), None)

        if user_to_login:
            password = self.handler.get_user_input("Enter user password: ")
            if Authentication.check_password(password=password, hashed=user_to_login.password):
                self.signed_up_user = user_to_login
                self.set_commands()
                self.handler.display_output(f"Welcome back, {user_name}!")
            else:
                self.handler.display_output("Invalid password.")
        else:
            self.handler.display_output("User name not found.")