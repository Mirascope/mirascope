"""A script for recommending movies."""
import os

from prompts import MovieRecommendationPrompt

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


def recommend_movies(genre: str):
    """Run the movie recommendation script."""
    return str(MovieRecommendationPrompt(genre=genre).create())


while True:
    genre = input("Enter genre: ")
    if genre == "quit":
        break
    print(recommend_movies(genre))
