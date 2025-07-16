import unittest
import pandas as pd
import json
import os
import tempfile
from unittest.mock import Mock, patch, mock_open
import bcrypt

# Import your classes
from user_movies_table import User_movie_table, Columns
from users import User, Authentication
from Handlers import CLIIOHandler, BaseIOHandler


class TestCLIIOHandler(unittest.TestCase):
    def setUp(self):
        self.handler = CLIIOHandler()

    @patch('builtins.input', return_value='test input')
    def test_get_user_input(self, mock_input):
        result = self.handler.get_user_input("Enter something: ")
        self.assertEqual(result, 'test input')
        mock_input.assert_called_once_with("Enter something: ")

    @patch('builtins.print')
    def test_display_output_args(self, mock_print):
        self.handler.display_output("Hello", "World")
        self.assertEqual(mock_print.call_count, 2)
        mock_print.assert_any_call("Hello")
        mock_print.assert_any_call("World")

    @patch('builtins.print')
    def test_display_output_kwargs(self, mock_print):
        self.handler.display_output(name="John", age=25)
        self.assertEqual(mock_print.call_count, 2)


class TestAuthentication(unittest.TestCase):
    def test_hash_password(self):
        password = "TestPassword123!"
        hashed = Authentication.hash_password(password)
        self.assertIsInstance(hashed, bytes)
        self.assertTrue(len(hashed) > 0)

    def test_check_password_correct(self):
        password = "TestPassword123!"
        hashed = Authentication.hash_password(password)
        result = Authentication.check_password(password, hashed)
        self.assertTrue(result)

    def test_check_password_incorrect(self):
        password = "TestPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = Authentication.hash_password(password)
        result = Authentication.check_password(wrong_password, hashed)
        self.assertFalse(result)

    def test_get_valid_password_valid_first_try(self):
        mock_handler = Mock()
        mock_handler.get_user_input.return_value = "ValidPass123!"

        result = Authentication.get_valid_password(mock_handler)

        self.assertEqual(result, "ValidPass123!")
        mock_handler.get_user_input.assert_called_once_with("Enter a valid password: ")
        mock_handler.display_output.assert_called_once_with("Password accepted.")

    def test_get_valid_password_invalid_then_valid(self):
        mock_handler = Mock()
        mock_handler.get_user_input.side_effect = ["weak", "ValidPass123!"]

        result = Authentication.get_valid_password(mock_handler)

        self.assertEqual(result, "ValidPass123!")
        self.assertEqual(mock_handler.get_user_input.call_count, 2)


class TestUser(unittest.TestCase):
    def setUp(self):
        # Reset global counter for consistent testing
        import config
        config.global_users_amount = 0

    def test_user_init(self):
        user = User("testuser", "TestPassword123!")
        self.assertEqual(user.user_name, "testuser")
        self.assertEqual(user.id, 0)
        self.assertIsInstance(user.movies_table, User_movie_table)
        self.assertIsInstance(user.password, bytes)

    def test_user_init_increments_global_counter(self):
        user1 = User("user1", "TestPassword123!")
        user2 = User("user2", "TestPassword123!")
        self.assertEqual(user1.id, 0)
        self.assertEqual(user2.id, 1)

    @patch('users.Authentication.get_valid_password')
    def test_create_from_user_input(self, mock_get_valid):
        mock_get_valid.return_value = "ValidPass123!"
        mock_handler = Mock()
        mock_handler.get_user_input.return_value = "testuser"

        user = User.create_from_user_input(mock_handler)

        self.assertEqual(user.user_name, "testuser")
        mock_handler.get_user_input.assert_called_once_with("Please enter you user name: ")
        mock_get_valid.assert_called_once()

    @patch('users.Authentication.get_valid_password')
    def test_generate_password_no_param(self, mock_get_valid):
        mock_get_valid.return_value = "ValidPass123!"
        mock_handler = Mock()

        user = User("testuser", handler=mock_handler)

        mock_get_valid.assert_called_once_with(mock_handler)
        self.assertIsInstance(user.password, bytes)


class TestUserMovieTable(unittest.TestCase):
    def setUp(self):
        self.table = User_movie_table(1)
        self.handler = Mock()

    def test_init(self):
        table = User_movie_table(1)
        self.assertEqual(table.user_id, 1)
        self.assertIsInstance(table.df, pd.DataFrame)
        self.assertIsInstance(table.handler, CLIIOHandler)

    def test_create_from_json_valid_file(self):
        test_data = {
            "user_id": 1,
            "movies_data": [
                {"name": "Movie1", "rank": 8, "genre": "Action"},
                {"name": "Movie2", "rank": 6, "genre": "Comedy"}
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            handler = Mock()
            table = User_movie_table.create_from_json(temp_file, handler)

            self.assertIsNotNone(table)
            self.assertEqual(table.user_id, 1)
            self.assertEqual(len(table.df), 2)
            self.assertEqual(table.df.iloc[0]['name'], 'Movie1')
        finally:
            os.unlink(temp_file)

    def test_create_from_json_invalid_file(self):
        handler = Mock()
        table = User_movie_table.create_from_json("nonexistent.json", handler)

        self.assertIsNone(table)
        handler.display_output.assert_called_once_with("Invalid file path.")

    def test_get_movie_rank_valid_input(self):
        with patch.object(self.table.handler, 'get_user_input', return_value='8'):
            rank = self.table._get_movie_rank("Test Movie")
            self.assertEqual(rank, 8)

    def test_get_movie_rank_invalid_input(self):
        with patch.object(self.table.handler, 'get_user_input', return_value='invalid'):
            with patch.object(self.table.handler, 'display_output'):
                rank = self.table._get_movie_rank("Test Movie")
                self.assertEqual(rank, 5)

    def test_get_movie_rank_out_of_range(self):
        with patch.object(self.table.handler, 'get_user_input', return_value='15'):
            with patch.object(self.table.handler, 'display_output'):
                rank = self.table._get_movie_rank("Test Movie")
                self.assertEqual(rank, 5)

    def test_get_movie_genre(self):
        with patch.object(self.table.handler, 'get_user_input', return_value='Action'):
            genre = self.table._get_movie_genre("Test Movie")
            self.assertEqual(genre, "Action")

    def test_add_movies_from_user(self):
        inputs = ["Movie1", "8", "Action", "Movie2", "6", "Comedy", "quit"]
        with patch.object(self.table.handler, 'get_user_input', side_effect=inputs):
            self.table.add_movies_from_user()
            self.assertEqual(len(self.table.df), 2)
            self.assertEqual(self.table.df.iloc[0]['name'], 'Movie1')
            self.assertEqual(self.table.df.iloc[1]['name'], 'Movie2')

    def test_get_best_movie(self):
        # Add test data
        test_data = pd.DataFrame([
            {'name': 'Movie1', 'rank': 8, 'genre': 'Action', 'user_id': 1},
            {'name': 'Movie2', 'rank': 6, 'genre': 'Comedy', 'user_id': 1},
            {'name': 'Movie3', 'rank': 9, 'genre': 'Drama', 'user_id': 1}
        ])
        self.table.df = test_data

        best_movie, best_rank = self.table.get_best_movie()
        self.assertEqual(best_movie, 'Movie3')
        self.assertEqual(best_rank, 9)

    def test_get_worst_movie(self):
        # Add test data
        test_data = pd.DataFrame([
            {'name': 'Movie1', 'rank': 8, 'genre': 'Action', 'user_id': 1},
            {'name': 'Movie2', 'rank': 6, 'genre': 'Comedy', 'user_id': 1},
            {'name': 'Movie3', 'rank': 9, 'genre': 'Drama', 'user_id': 1}
        ])
        self.table.df = test_data

        worst_movie, worst_rank = self.table.get_worst_movie()
        self.assertEqual(worst_movie, 'Movie2')
        self.assertEqual(worst_rank, 6)

    def test_get_avg_ranking(self):
        # Add test data
        test_data = pd.DataFrame([
            {'name': 'Movie1', 'rank': 8, 'genre': 'Action', 'user_id': 1},
            {'name': 'Movie2', 'rank': 6, 'genre': 'Comedy', 'user_id': 1},
            {'name': 'Movie3', 'rank': 9, 'genre': 'Drama', 'user_id': 1}
        ])
        self.table.df = test_data

        avg_rank = self.table.get_avg_ranking()
        self.assertEqual(avg_rank, 7.67)  # (8+6+9)/3 = 7.67

    def test_print_basic_stats(self):
        # Add test data
        test_data = pd.DataFrame([
            {'name': 'Movie1', 'rank': 8, 'genre': 'Action', 'user_id': 1},
            {'name': 'Movie2', 'rank': 6, 'genre': 'Comedy', 'user_id': 1},
            {'name': 'Movie3', 'rank': 9, 'genre': 'Drama', 'user_id': 1}
        ])
        self.table.df = test_data

        with patch.object(self.table.handler, 'display_output') as mock_display:
            self.table.print_basic_stats()
            self.assertEqual(mock_display.call_count, 3)

    def test_are_similar_identical_tables(self):
        # Create two identical tables
        table1 = User_movie_table(1)
        table2 = User_movie_table(2)

        test_data = pd.DataFrame([
            {'name': 'Movie1', 'rank': 8, 'genre': 'Action', 'user_id': 1},
            {'name': 'Movie2', 'rank': 6, 'genre': 'Comedy', 'user_id': 1}
        ])
        table1.df = test_data.copy()
        table2.df = test_data.copy()

        result = User_movie_table.are_similar(table1, table2)
        self.assertTrue(result)

    def test_are_similar_different_genres(self):
        # Create tables with different genres
        table1 = User_movie_table(1)
        table2 = User_movie_table(2)

        table1.df = pd.DataFrame([
            {'name': 'Movie1', 'rank': 8, 'genre': 'Action', 'user_id': 1}
        ])
        table2.df = pd.DataFrame([
            {'name': 'Movie2', 'rank': 8, 'genre': 'Comedy', 'user_id': 2}
        ])

        result = User_movie_table.are_similar(table1, table2)
        self.assertFalse(result)

    def test_are_similar_large_rank_difference(self):
        # Create tables with large rank differences
        table1 = User_movie_table(1)
        table2 = User_movie_table(2)

        table1.df = pd.DataFrame([
            {'name': 'Movie1', 'rank': 8, 'genre': 'Action', 'user_id': 1}
        ])
        table2.df = pd.DataFrame([
            {'name': 'Movie2', 'rank': 2, 'genre': 'Action', 'user_id': 2}
        ])

        result = User_movie_table.are_similar(table1, table2)
        self.assertFalse(result)  # Difference of 6 > 0.5

    def test_get_movie_recommendation_empty_df(self):
        # Test with empty dataframe
        with patch.object(self.table.handler, 'display_output') as mock_display:
            self.table.get_movie_recommendation()
            mock_display.assert_called_once_with(
                "No movies available for recommendations. Please add some movies first.")

    def test_movies_recommendations_based_on_similarity(self):
        # Create similar tables
        table1 = User_movie_table(1)
        table2 = User_movie_table(2)

        table1.df = pd.DataFrame([
            {'name': 'Movie1', 'rank': 8, 'genre': 'Action', 'user_id': 1}
        ])
        table2.df = pd.DataFrame([
            {'name': 'Movie1', 'rank': 8, 'genre': 'Action', 'user_id': 2},
            {'name': 'Movie2', 'rank': 9, 'genre': 'Action', 'user_id': 2}
        ])

        handler = Mock()
        with patch.object(User_movie_table, 'are_similar', return_value=True):
            User_movie_table.movies_recommendations_based_on_similarity(table1, table2, handler)

            # Should recommend Movie2 since it's not in table1 and has rank > 8
            handler.display_output.assert_any_call("Here are some recommendations for movies you may like: ")
            handler.display_output.assert_any_call("Movie2")

    def test_to_json(self):
        # Add test data
        test_data = pd.DataFrame([
            {'name': 'Movie1', 'rank': 8, 'genre': 'Action', 'user_id': 1}
        ])
        self.table.df = test_data

        with patch('builtins.open', mock_open()) as mock_file:
            with patch('json.dump') as mock_json_dump:
                self.table.to_json()

                mock_file.assert_called_once_with("user_1_data", "w")
                mock_json_dump.assert_called_once()


class TestColumns(unittest.TestCase):
    def test_column_values(self):
        self.assertEqual(Columns.Name.value, 'name')
        self.assertEqual(Columns.Rank.value, 'rank')
        self.assertEqual(Columns.Genre.value, 'genre')
        self.assertEqual(Columns.User_ID.value, 'user_id')
        self.assertEqual(Columns.JSON_USER_ID.value, 'user_id')
        self.assertEqual(Columns.JSON_MOVIES_DATA.value, 'movies_data')


class TestIntegration(unittest.TestCase):
    def setUp(self):
        import config
        config.global_users_amount = 0

    def test_user_with_movie_table_integration(self):
        # Create a user with a password to avoid the infinite loop
        user = User("testuser", "TestPassword123!")

        # Add a movie to their table
        test_data = pd.DataFrame([
            {'name': 'Movie1', 'rank': 8, 'genre': 'Action', 'user_id': user.id}
        ])
        user.movies_table.df = test_data

        # Test basic functionality
        best_movie, best_rank = user.movies_table.get_best_movie()
        self.assertEqual(best_movie, 'Movie1')
        self.assertEqual(best_rank, 8)
        self.assertEqual(user.movies_table.user_id, user.id)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)