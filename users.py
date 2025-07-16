from typing import List, Dict, Tuple, Optional
import config
from user_movies_table import User_movie_table
import re
import bcrypt
from Handlers import CLIIOHandler


class Authentication:
    @classmethod
    def hash_password(cls, password: str) -> bytes:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed

    @classmethod
    def check_password(cls, password: str, hashed: bytes) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed)

    @classmethod
    def get_valid_password(cls, handler: CLIIOHandler):
        pattern = re.compile(
            r'^(?=.*[a-z])'  # at least one lowercase letter
            r'(?=.*[A-Z])'  # at least one uppercase letter
            r'(?=.*\d)'  # at least one digit
            r'(?=.*[@$!%*?&#^()_+=\-{}\[\]:;"\'<>,./\\|`~])'  # at least one special character
            r'.{8,}$'  # at least 8 characters
        )

        while True:
            password = handler.get_user_input("Enter a valid password: ")
            if pattern.match(password):
                handler.display_output("Password accepted.")
                return password
            else:
                handler.display_output("Invalid password. Must be at least 8 characters long and include:")
                handler.display_output(" - at least one lowercase letter")
                handler.display_output(" - at least one uppercase letter")
                handler.display_output(" - at least one number")
                handler.display_output(" - at least one special character")


class User:
    def __init__(self, user_name, password=None, handler=None):
        self.user_name = user_name
        self.password = self.generate_password(password, handler)
        self.id = config.global_users_amount
        self.movies_table = User_movie_table(self.id)
        config.global_users_amount += 1

    @classmethod
    def create_from_user_input(cls, handler: CLIIOHandler):
        user_name = handler.get_user_input("Please enter you user name: ")
        return cls(user_name, handler=handler)

    def generate_password(self, password=None, handler=None):
        """
        Generates password for the user by using the argument/asking for it and then hashing it
        :param password: Optional password
        :param handler: Optional handler for input/output
        :return: hashed password
        """
        if password is None:
            if handler is None:
                handler = CLIIOHandler()
            password = Authentication.get_valid_password(handler)
        return Authentication.hash_password(password)




