import json
from enum import Enum
from typing import Tuple
from colorama import init, Fore, Style
import pandas as pd
from Handlers import CLIIOHandler, BaseIOHandler

BEST_MOVIE_STR = "The best movie is {name} with the rank of {rank}"
WORST_MOVIE_STR = "The worst movie is {name} with the rank of {rank}"
AVG_RANK_STR = "The average rank of the movies is {avg}"


class Columns(Enum):
    Name = 'name'
    Rank = 'rank'
    Genre = 'genre'
    User_ID = 'user_id'
    JSON_USER_ID = 'user_id'
    JSON_MOVIES_DATA = 'movies_data'
    Similarity_Treshold = 0.5
    Recommendation_Rating = 8


init()


class User_movie_table:
    def __init__(self, user_id: int, handler=CLIIOHandler()):
        self.user_id = user_id
        self.df = pd.DataFrame(
            columns=[Columns.Name.value, Columns.Rank.value, Columns.Genre.value, Columns.User_ID.value])
        self.handler = handler

    @classmethod
    def create_from_json(cls, path: str, handler=CLIIOHandler()):
        try:
            with open(path, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            handler.display_output("JSON file not found.")
            return None
        else:
            instance = cls(data[Columns.JSON_USER_ID.value])
            instance.df = pd.DataFrame(data[Columns.JSON_MOVIES_DATA.value])
            return instance

    def _get_movie_rank(self, movie_name: str) -> int:
        rank_str = self.handler.get_user_input(f"Please enter you rank for the movie {movie_name} from 1-10: ")
        try:
            rank = int(rank_str)
            if not 1 <= rank <= 10:
                raise ValueError
        except (ValueError, TypeError):
            self.handler.display_output("Invalid input. Sets rank to 5")
            rank = 5
        return rank

    def add_movies_from_user(self):
        while True:
            movie_name = self.handler.get_user_input("Please enter a movie name (or 'quit' to finish): ")
            if movie_name.lower() == 'quit':
                break
            rank = self._get_movie_rank(movie_name)
            genre = self.handler.get_user_input(f"Please enter the genre of the movie {movie_name}: ")
            new_row = {
                Columns.Name.value: movie_name,
                Columns.Rank.value: rank,
                Columns.Genre.value: genre,
                Columns.User_ID.value: self.user_id
            }
            new_row_df = pd.DataFrame([new_row])
            self.df = pd.concat([self.df, new_row_df], ignore_index=True)

    def get_best_movie(self) -> Tuple[str, int]:
        temp_df = self.df.sort_values(by=Columns.Rank.value, ascending=False)
        return temp_df.iloc[0][Columns.Name.value], temp_df.iloc[0][Columns.Rank.value]

    def get_worst_movie(self) -> Tuple[str, int]:
        temp_df = self.df.sort_values(by=Columns.Rank.value, ascending=True)
        return temp_df.iloc[0][Columns.Name.value], temp_df.iloc[0][Columns.Rank.value]

    def get_avg_ranking(self) -> float:
        return round(self.df[Columns.Rank.value].mean(), 2)

    def print_basic_stats(self) -> None:
        if self.df.empty:
            self.handler.display_output("No movies in the list to calculate stats.")
            return

        best_movie = self.get_best_movie()
        best_movie_str = BEST_MOVIE_STR.format(name=best_movie[0], rank=best_movie[1])

        worst_movie = self.get_worst_movie()
        worst_movie_str = WORST_MOVIE_STR.format(name=worst_movie[0], rank=worst_movie[1])

        avg_movie = self.get_avg_ranking()
        avg_movie_str = AVG_RANK_STR.format(avg=avg_movie)

        self.handler.display_output(Fore.GREEN + best_movie_str + Style.RESET_ALL)
        self.handler.display_output(Fore.RED + worst_movie_str + Style.RESET_ALL)
        self.handler.display_output(Fore.YELLOW + avg_movie_str + Style.RESET_ALL)

    @classmethod
    def _get_movie_recommendation(cls, movies_df: pd.DataFrame, handler=CLIIOHandler()) -> None:
        if movies_df.empty:
            handler.display_output("No more movies available for recommendations.")
            return

        available_genres = movies_df[Columns.Genre.value].unique()
        handler.display_output(f"Available genres: {', '.join(available_genres)}")
        genre = handler.get_user_input("Please enter the genre you're interested in: ")

        potential_movies = movies_df[movies_df[Columns.Genre.value].str.lower() == genre.lower()]
        current_recommendation = None

        if not potential_movies.empty:
            potential_movies = potential_movies.sort_values(by=Columns.Rank.value, ascending=False)
            current_recommendation = potential_movies.iloc[0]
            handler.display_output(f"Our best movie from {genre} genre is {current_recommendation[Columns.Name.value]} "
                                   f"with the rank of {current_recommendation[Columns.Rank.value]}")
        else:
            handler.display_output("We don't have any movies answering to this genre name.")

        another_recommendation = handler.get_user_input("Enter 'exit' to finish and any other input to proceed: ")
        if another_recommendation.lower() == 'exit':
            return

        if current_recommendation is not None:
            new_movies_df = movies_df.drop(current_recommendation.name)
            cls._get_movie_recommendation(new_movies_df, handler)
        else:
            cls._get_movie_recommendation(movies_df, handler)

    def get_movie_recommendation(self) -> None:
        if self.df.empty:
            self.handler.display_output("No movies available for recommendations. Please add some movies first.")
            return
        self._get_movie_recommendation(self.df.copy(), self.handler)

    @classmethod
    def are_similar(cls, table1: 'User_movie_table', table2: 'User_movie_table') -> bool:
        if table1.df.empty or table2.df.empty:
            return False

        first_genres_vector = table1.df.groupby(Columns.Genre.value)[Columns.Rank.value].mean()
        second_genres_vector = table2.df.groupby(Columns.Genre.value)[Columns.Rank.value].mean()

        if set(first_genres_vector.index) != set(second_genres_vector.index):
            return False

        diff = (first_genres_vector - second_genres_vector).abs()
        return diff.max() <= Columns.Similarity_Treshold.value

    @classmethod
    def movies_recommendations_based_on_similarity(cls, cls1, cls2, handler: CLIIOHandler) -> None:
        if not User_movie_table.are_similar(cls1, cls2):
            return

        sorted_df = cls2.df.sort_values(by=Columns.Rank.value, ascending=False)
        recommendations = []
        for _, row in sorted_df.iterrows():
            if (row[Columns.Name.value] not in cls1.df[Columns.Name.value].values and
                    row[Columns.Rank.value] > Columns.Recommendation_Rating.value):
                if len(recommendations) < 5:
                    recommendations.append(row[Columns.Name.value])
                else:
                    break

        if not recommendations:
            handler.display_output("There are no recommendations.")
        else:
            handler.display_output("Here are some recommendations for movies you may like: ")
            for title in recommendations:
                handler.display_output(title)

    def to_json(self):
        dict1 = {Columns.User_ID.value: self.user_id,
                 Columns.JSON_MOVIES_DATA.value: self.df.to_dict(orient="records")}
        with open(f"user_{self.user_id}_data.json", "w") as file:
            json.dump(dict1, file, indent=2)