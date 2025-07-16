import json
from enum import Enum, IntEnum
from typing import List, Dict, Tuple, Optional
from colorama import init, Fore, Style
import pandas as pd
from Handlers import CLIIOHandler

class Columns(Enum):
    Name = 'name'
    Rank = 'rank'
    Genre = 'genre'
    User_ID = 'user_id'
    JSON_USER_ID = 'user_id'
    JSON_MOVIES_DATA = 'movies_data'



init()
class User_movie_table:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.df = pd.DataFrame(columns=[Columns.Name.value, Columns.Rank.value, Columns.User_ID.value])
        self.handler = CLIIOHandler()


    @classmethod
    def create_from_json(cls, path: str, handler: CLIIOHandler):
        try:
            with open(path, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            handler.display_output("Invalid file path.")
            return None
        else:
            instance = cls(data[Columns.JSON_USER_ID.value])
            instance.df = pd.DataFrame(data[Columns.JSON_MOVIES_DATA.value])
            return instance


    def _get_movie_rank(self, movie_name: str) -> str:
        rank = self.handler.get_user_input(f"Please enter you rank for the movie {movie_name} from 1-10: ")
        try:
            rank = int(rank)
            if rank < 1 or rank > 10:
                raise ValueError
        except ValueError:
            self.handler.display_output("Invalid input. Sets rank to 5")
            rank = 5
        finally:
            return rank


    def _get_movie_genre(self, movie_name: str) -> str:
        genre = self.handler.get_user_input(f"Please enter the genre of the movie {movie_name}: ")
        return genre


    def add_movies_from_user(self):
        #move the movie name outside
        movie_name = self.handler.get_user_input("Please enter a movie name and enter quit to finish: ")
        while movie_name != 'quit':
            rank = self._get_movie_rank(movie_name)
            genre = self._get_movie_genre(movie_name)
            new_row_df = pd.DataFrame([{Columns.Name.value: movie_name, Columns.Rank.value: rank,
                                        Columns.Genre.value: genre, Columns.User_ID.value: self.user_id}])
            self.df = pd.concat([self.df, new_row_df], ignore_index=True)
            movie_name = self.handler.get_user_input("Please enter a movie name and enter quit to finish: ")


    def get_best_movie(self) -> Tuple[str, int]:
        temp_df = self.df.sort_values(by=Columns.Rank.value, ascending=False)
        return temp_df.iloc[0][Columns.Name.value], temp_df.iloc[0][Columns.Rank.value]


    def get_worst_movie(self) -> Tuple[str, int]:
        temp_df = self.df.sort_values(by=Columns.Rank.value, ascending=True)
        return temp_df.iloc[0][Columns.Name.value], temp_df.iloc[0][Columns.Rank.value]


    def get_avg_ranking(self) -> Tuple[str, int]:
        return round(self.df[Columns.Rank.value].mean(), 2)


    def print_basic_stats(self) -> None:
        # create print handler
        best_movie = self.get_best_movie()
        # turn into constants
        best_movie_str = f"The best movie is {best_movie[0]} with the rank of {best_movie[1]}"
        worst_movie = self.get_worst_movie()
        worst_movie_str = f"The worst movie is {worst_movie[0]} with the rank of {worst_movie[1]}"
        avg_movie = self.get_avg_ranking()
        avg_movie_str = f"The average rank of the movies is {avg_movie}"
        self.handler.display_output(Fore.GREEN + best_movie_str + Style.RESET_ALL)
        self.handler.display_output(Fore.RED + worst_movie_str + Style.RESET_ALL)
        self.handler.display_output(Fore.YELLOW + avg_movie_str + Style.RESET_ALL)


    @classmethod
    def _get_movie_recommendation(cls, movies_df: pd.DataFrame, handler: CLIIOHandler) -> None:
        """
        A recursive function that fetches from the user a genre and returns the
        best movie available in that genre.
        The user can keep asking for next recommendation as long as they want
        :param movies_df: current movies DataFrame
        """
        if movies_df.empty:
            handler.display_output("No more movies available for recommendations.")
            return

        available_genres = movies_df[Columns.Genre.value].unique()
        handler.display_output(f"Available genres: {', '.join(available_genres)}")

        genre = handler.get_user_input("Please enter the genre you're interested in: ")
        current_recommendation = None

        #Turn to regular if-else
        try:
            potential_movies = movies_df.loc[movies_df[Columns.Genre.value] == genre]
            if potential_movies.empty:
                raise IndexError
        except IndexError:
            handler.display_output("We don't have any movies answering to this genre name.")
        else:
            potential_movies = potential_movies.sort_values(by=Columns.Rank.value, ascending=False)
            current_recommendation = potential_movies.iloc[0]
            handler.display_output(f"Our best movie from {genre} genre is {current_recommendation[Columns.Name.value]}"
                  f" with the rank of {current_recommendation[Columns.Rank.value]}")

        another_recommendation = handler.get_user_input("Enter 'exit' to finish "
                                       "and any other input to proceed to next recommendation: ")
        if another_recommendation == 'exit':
            return
        elif current_recommendation is not None:
            new_movies_df = movies_df.drop(current_recommendation.name)  # Fixed: use .name instead of .index
            cls._get_movie_recommendation(new_movies_df)
        else:
            cls._get_movie_recommendation(movies_df)


    def get_movie_recommendation(self) -> None:
        if self.df.empty:
            self.handler.display_output("No movies available for recommendations. Please add some movies first.")
            return
        return self._get_movie_recommendation(self.df.copy(), CLIIOHandler())  # Use copy to avoid modifying original


    @classmethod
    def are_similar(cls, cls1:'User_movie_table', cls2:'User_movie_table') -> bool:
        """
        class method that checks if two tables are 'similar'
        'similar' == the delta between the average genre rank for each genre is less then 0.5
        Also, the genres in each table have to be identical
        :param cls2: movies table to compare with
        :return: True if similar, False otherwise
        """
        # Step 1 - Create the genre vector for each table (pd series)
        first_genres_vector = cls1.df.groupby(Columns.Genre.value)[Columns.Rank.value].mean()
        first_genres = list(first_genres_vector.index)
        second_genres_vector = cls2.df.groupby(Columns.Genre.value)[Columns.Rank.value].mean()
        second_genres = list(second_genres_vector.index)
        # Step 2 - Check similarity
        if set(first_genres) != set(second_genres):
            return False
        first_genres.sort()
        second_genres.sort()
        for i in range(len(first_genres)):
            first_genre_rank = first_genres_vector.loc[first_genres[i]]
            second_genre_rank = second_genres_vector.loc[second_genres[i]]
            if abs(first_genre_rank - second_genre_rank) > 0.5:
                return False
        return True


    @classmethod
    def movies_recommendations_based_on_similarity(cls, cls1, cls2, handler: CLIIOHandler) -> None:
        """
        print recommendations from the second instance's table that weren't watched in the first instance's table
        only if both instances are similar
        """
        if not User_movie_table.are_similar(cls1, cls2):
            return
        # Step 1 - sort the movies in the second table by popularity
        sorted_df = cls2.df.sort_values(by=Columns.Rank.value, ascending=False)
        # Step 2 - iterate through the sorted movies and collect all movie names with rank above 8
        #           that are not exist in the first table, and top amount of 5 recommendations
        recommendations = 0
        recommendations_list = []
        for index, row in sorted_df.iterrows():
            if row[Columns.Name.value] not in cls1.df[Columns.Name.value].values and row[Columns.Rank.value] > 8:
                recommendations += 1
                recommendations_list.append(row[Columns.Name.value])
            if recommendations == 5:
                break
        # Step 3 - Print the recommendations
        if recommendations == 0:
            handler.display_output("There are no recommendations.")
        else:
            handler.display_output("Here are some recommendations for movies you may like: ")
            for title in recommendations_list:
                handler.display_output(title)

    def to_json(self):
        dict1 = {Columns.User_ID.value: self.user_id,
                 Columns.JSON_MOVIES_DATA.value: self.df.to_dict(orient="records")}
        with open(f"user_{self.user_id}_data", "w") as file:
            json.dump(dict1, file, indent=2)

