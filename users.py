from typing import List, Dict, Tuple, Optional
import config
from user_movies_table import User_movie_table
import re
import bcrypt

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
    def get_valid_password(cls):
        pattern = re.compile(
            r'^(?=.*[a-z])'  # at least one lowercase letter
            r'(?=.*[A-Z])'  # at least one uppercase letter
            r'(?=.*\d)'  # at least one digit
            r'(?=.*[@$!%*?&#^()_+=\-{}\[\]:;"\'<>,./\\|`~])'  # at least one special character
            r'.{8,}$'  # at least 8 characters
        )

        while True:
            password = input("Enter a valid password: ")
            if pattern.match(password):
                print("Password accepted.")
                return password
            else:
                print("Invalid password. Must be at least 8 characters long and include:")
                print(" - at least one lowercase letter")
                print(" - at least one uppercase letter")
                print(" - at least one number")
                print(" - at least one special character")


class User:
    def __init__(self, user_name, password=None):
        self.user_name = user_name
        self.password = self.generate_password(password)
        self.id = config.global_users_amount
        self.movies_table = User_movie_table(self.id)
        config.global_users_amount += 1


    @classmethod
    def create_from_user_input(cls):
        user_name = input("Please enter you user name: ")
        return cls(user_name)


    @classmethod
    def generate_password(cls, password=None):
        """
        Generates password for the user by using the argument/asking for it and then hashing it
        :param password: Optional password
        :return: hashed password
        """
        if password is None:
            password = Authentication.get_valid_password()
        return Authentication.hash_password(password)



