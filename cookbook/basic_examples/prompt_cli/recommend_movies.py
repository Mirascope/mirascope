"""A script for recommending movies."""
import os

from movie_prompts import MovieRecommendationPrompt

from mirascope import OpenAIChat

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


def recommend_movies(genre: str):
    """Run the movie recommendation script."""
    model = OpenAIChat()
    return str(model.create(MovieRecommendationPrompt(genre=genre)))


while True:
    genre = input("Enter genre: ")
    if genre == "quit":
        break
    print(recommend_movies(genre))
