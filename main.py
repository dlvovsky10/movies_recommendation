from typing import List, Dict, Tuple, Optional
from user_movies_table import User_movie_table
from config import global_users_amount
import pandas as pd

def main():
    tbl1 = {'name': ['ex1', 'ex2', 'ex3'], 'rank': [8.5, 9.5 ,5], 'genre': ['scifi', 'horror', 'drama'], 'user_id': [3, 3, 3]}
    first_table = User_movie_table(3)
    first_table.df = pd.DataFrame(tbl1)
    tbl2 = {'name': ['dug1', 'dug2', 'dug3'], 'rank': [9, 9.75 ,5], 'genre': ['scifi', 'horror', 'drama'], 'user_id': [4, 4, 4]}
    second_table = User_movie_table(4)
    second_table.df = pd.DataFrame(tbl2)
    User_movie_table.movies_recommendations_based_on_similarity(first_table, second_table)
    first_table.to_json()
    # third_table = User_movie_table.create_from_json("user_3_data")
    # third_table.user_id = 4
    # third_table.to_json()


if __name__ == "__main__":
    main()
