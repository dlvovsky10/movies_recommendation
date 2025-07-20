import pytest
import pandas as pd
from typing import List

# Import classes from the application files
from Handlers import BaseIOHandler
from users import User, Authentication
from user_movies_table import User_movie_table
from Game import Game


# Mock IO Handler for automated testing
class MockIOHandler(BaseIOHandler):
    def __init__(self, inputs: List[str] = None):
        self.inputs = inputs or []
        self.outputs = []
        self._input_idx = 0

    def get_user_input(self, message=""):
        if self._input_idx < len(self.inputs):
            user_input = self.inputs[self._input_idx]
            self._input_idx += 1
            return user_input
        raise ValueError("Not enough mock inputs provided for test.")

    def display_output(self, *args, **kwargs):
        if args:
            self.outputs.append(str(args[0]))

    def last_output(self):
        return self.outputs[-1] if self.outputs else ""

    def all_output(self):
        return "\n".join(self.outputs)


# --- Test Fixtures ---
@pytest.fixture
def valid_password():
    return "ValidPass123!"


@pytest.fixture
def user_a(valid_password):
    return User(user_name="Alice", user_id=0, password=valid_password)


# --- Test Cases ---

def test_password_hashing_and_checking(valid_password):
    """Tests if password hashing and verification work correctly."""
    hashed_password = Authentication.hash_password(valid_password)
    assert isinstance(hashed_password, bytes)
    assert Authentication.check_password(valid_password, hashed_password)
    assert not Authentication.check_password("WrongPass123!", hashed_password)


class TestUserMovieTable:
    """Tests the functionality of the User_movie_table class."""

    def test_stats_on_empty_table(self):
        """Tests that stats function reports correctly for an empty table."""
        handler = MockIOHandler()
        table = User_movie_table(user_id=0, handler=handler)
        table.print_basic_stats()
        assert "No movies in the list" in handler.last_output()

    def test_stats_on_valid_table(self):
        """Tests calculation of best, worst, and average ranks."""
        handler = MockIOHandler()
        table = User_movie_table(user_id=0, handler=handler)
        table.df = pd.DataFrame([
            {'name': 'Inception', 'rank': 10, 'genre': 'Sci-Fi', 'user_id': 0},
            {'name': 'Titanic', 'rank': 6, 'genre': 'Romance', 'user_id': 0},
            {'name': 'The Room', 'rank': 1, 'genre': 'Drama', 'user_id': 0}
        ])

        name, rank = table.get_best_movie()
        assert name == 'Inception' and rank == 10

        name, rank = table.get_worst_movie()
        assert name == 'The Room' and rank == 1

        avg = table.get_avg_ranking()
        assert avg == pytest.approx(5.67)

    def test_are_similar_true(self):
        """Tests if two tables with similar genre averages are correctly identified."""
        table1 = User_movie_table(0)
        table1.df = pd.DataFrame([
            {'name': 'A', 'rank': 8, 'genre': 'G1', 'user_id': 0},
            {'name': 'B', 'rank': 6, 'genre': 'G2', 'user_id': 0}
        ])
        table2 = User_movie_table(1)
        table2.df = pd.DataFrame([
            {'name': 'C', 'rank': 8.4, 'genre': 'G1', 'user_id': 1},
            {'name': 'D', 'rank': 5.6, 'genre': 'G2', 'user_id': 1}
        ])
        assert User_movie_table.are_similar(table1, table2)

    def test_are_similar_false_diff_ranks(self):
        """Tests that tables with >0.5 rank difference are not similar."""
        table1 = User_movie_table(0)
        table1.df = pd.DataFrame([{'name': 'A', 'rank': 8, 'genre': 'G1', 'user_id': 0}])
        table2 = User_movie_table(1)
        table2.df = pd.DataFrame([{'name': 'C', 'rank': 7.4, 'genre': 'G1', 'user_id': 1}])
        assert not User_movie_table.are_similar(table1, table2)


class TestGame:
    """Tests the main game logic and user interaction flow."""

    def test_signup_and_username_taken(self, valid_password):
        """Tests user signup and ensures duplicate usernames are rejected."""
        # FIX: Added "8" to handle logging out after the first signup.
        inputs = ["2", "testuser", valid_password, "8", "2", "testuser", "3"]
        handler = MockIOHandler(inputs)
        game = Game(handler)
        game.show_main_menu()

        output = handler.all_output()
        assert "Welcome testuser!" in output
        assert "Logging out testuser..." in output
        assert "This username is already taken" in output
        assert len(game.users) == 1

    def test_login_logout(self, valid_password):
        """Tests that a user can successfully log in and log out."""
        # Manually create a user to test login
        game = Game(MockIOHandler([]))
        game.users.append(User("testuser", 0, password=valid_password))

        # New handler with inputs for the test run
        run_handler = MockIOHandler(["1", "testuser", valid_password, "8", "3"])
        game.handler = run_handler
        game.show_main_menu()

        output = run_handler.all_output()
        assert "Welcome back, testuser!" in output
        assert "Logging out testuser..." in output

    def test_login_fail(self, valid_password):
        """Tests login failures for non-existent users and wrong passwords."""
        handler = MockIOHandler(["1", "no_user", "1", "testuser", "WrongPass!", "3"])
        game = Game(handler)
        game.users.append(User("testuser", 0, password=valid_password))

        game.show_main_menu()
        output = handler.all_output()
        assert "User name not found" in output
        assert "Invalid password" in output