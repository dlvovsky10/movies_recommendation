from typing import List, Dict, Tuple, Optional
import pandas as pd

def get_movies() -> List[str]:
    movies = []
    movie_name = input("Please enter a movie name and enter quit to finish")
    while movie_name != 'quit':
        movies.append(movie_name)
        movie_name = input("Please enter a movie name and enter quit to finish")
    return movies

def rank_movies(movies: List[str]) -> Dict[str, int]:
    """
    Getting the ranks from the user, if gets invalid input sets it to be 5
    :param movies:
    :return:
    """
    print("We are going to rank all movies you inserted")
    ranked_movies = {}
    for movie in movies:
        rank = (f"Enter you rank for the movie {movie} from 1-10: ")
        try:
            rank = int(rank)
        except ValueError:
            print("Invalid input. Sets rank to 5")
            rank = 5
        finally:
            ranked_movies[movie] = rank
    return ranked_movies

def get_best_movie(
        movies_df: Optional[pd.DataFrame] = None,
        movies_dict: Optional[Dict] = None):
    """
    Prefer to get a DataFrame but creates it if there isn't
    Have to get a dataFrame or a dictionary
    """
    if movies_df is None:
        if movies_dict is None:
            raise TypeError
        else:
            movies_df = pd.DataFrame(movies_dict)

    temp_df = movies_df.sort_values()