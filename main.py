from typing import List, Dict, Tuple, Optional
from colorama import init, Fore, Style
import pandas as pd

users_amount = 0
init()

def get_movies_from_user_from_user() -> List[str]:
    movies = []
    movie_name = input("Please enter a movie name and enter quit to finish: ")
    while movie_name != 'quit':
        movies.append(movie_name)
        movie_name = input("Please enter a movie name and enter quit to finish: ")
    return movies


def rank_movies_with_user(movies: List[str]) -> Dict[str, int]:
    """
    Getting the ranks from the user, if gets invalid input sets it to be 5
    """
    print("We are going to rank all movies you inserted")
    ranked_movies = {}
    for movie in movies:
        rank = input(f"Enter you rank for the movie {movie} from 1-10: ")
        try:
            rank = int(rank)
            if rank < 1 or rank > 10:
                raise ValueError
        except ValueError:
            print("Invalid input. Sets rank to 5")
            rank = 5
        finally:
            ranked_movies[movie] = rank
    return ranked_movies


def add_genres_with_user(movies_df: pd.DataFrame):
    """
    Get Genre for each movie from the user
    :param movies_df: Dataframe with movies details
    """
    genres = []
    for index, row in movies_df.iterrows():
        genre = input(f"Please enter the genre of the movie {row['name']}: ")
        genres.append(genre)
    movies_df['genre'] = genres


def movies_data_frame_transformation(
        movies_df: Optional[pd.DataFrame] = None,
        movies_dict: Optional[Dict] = None):
    """
    Prefer to get a DataFrame but creates it if there isn't
    Have to get a dataFrame or a dictionary
    """
    global users_amount
    if movies_df is None:
        if movies_dict is None:
            raise TypeError
        else:
            movies_df = pd.DataFrame(list(movies_dict.items()), columns=['name', 'rank'])

    movies_df['user_id'] = [users_amount for i in range(len(movies_df))]
    users_amount += 1
    return movies_df


def get_best_movie(
        movies_df: Optional[pd.DataFrame] = None,
        movies_dict: Optional[Dict] = None):
    if movies_df is None:
        movies_df = movies_data_frame_transformation(movies_df, movies_dict)
    temp_df = movies_df.sort_values(by='rank', ascending=False)
    return f"The best movie is {temp_df.iloc[0]['name']} with the rank of {temp_df.iloc[0]['rank']}"


def get_worst_movie(
        movies_df: Optional[pd.DataFrame] = None,
        movies_dict: Optional[Dict] = None):
    if movies_df is None:
        movies_df = movies_data_frame_transformation(movies_df, movies_dict)
    temp_df = movies_df.sort_values(by='rank', ascending=True)
    return f"The worst movie is {temp_df.iloc[0]['name']} with the rank of {temp_df.iloc[0]['rank']}"


def get_avg_ranking(
        movies_df: Optional[pd.DataFrame] = None,
        movies_dict: Optional[Dict] = None):
    if movies_df is None:
        movies_df = movies_data_frame_transformation(movies_df, movies_dict)
    avg = round(movies_df['rank'].mean(), 2)
    return f"The average rank of the movies is {avg}"

def get_movie_recommendation(movies_df: pd.DataFrame):
    """
    A recursive function that fetches from the user a genre and returns the
    best movie available in that genre.
    The user can keep asking for next recommendation as long as they want
    :param movies_df: current movies DataFrame
    """
    genre = input("Please enter the genre you're interested in: ")
    current_recommendation = None
    try:
        potential_movies = movies_df.loc[movies_df['genre'] == genre]
        if potential_movies.empty:
            raise IndexError
    except IndexError:
        print("We don't have any movies answering to this genre name.")
    else:
        potential_movies = potential_movies.sort_values(by='rank', ascending=False)
        current_recommendation = potential_movies.iloc[0]
        print(f"Our best movie from {genre} genre is {current_recommendation['name']}"
              f" with the rank of {current_recommendation['rank']}")
    finally:
        another_recommendation = input("Enter 'exit' to finish "
                                       "and any other input to proceed to next recommendation")
        if another_recommendation == 'exit':
            return
        elif current_recommendation is not None:
            new_movies_df = movies_df.drop(index=current_recommendation.index)
            get_movie_recommendation(new_movies_df)
        else:
            get_movie_recommendation(movies_df)


def main():
    # 1
    movies_list = get_movies_from_user_from_user()
    print("Movies List")
    print(movies_list)
    # 2
    ranked_movies = rank_movies_with_user(movies_list)
    # 3
    movies_df = movies_data_frame_transformation(movies_dict=ranked_movies)
    best_movie = get_best_movie(movies_df)
    worst_movie = get_worst_movie(movies_df)
    avg_ranking = get_avg_ranking(movies_df)
    print(Fore.GREEN + best_movie + Style.RESET_ALL)
    print(Fore.RED + worst_movie + Style.RESET_ALL)
    print(Fore.YELLOW + avg_ranking + Style.RESET_ALL)
    # 4
    add_genres_with_user(movies_df)
    # 5
    get_movie_recommendation(movies_df)

if __name__ == "__main__":
    main()
