"""A script for recommending movies."""
import os

from dotenv import load_dotenv
from prompts import MovieRecommendationPrompt

from mirascope import OpenAIChat

load_dotenv()


def recommend_movies(genre: str):
    """Run the movie recommendation script."""
    model = OpenAIChat(api_key=os.getenv("OPENAI_API_KEY"))
    return str(model.create(MovieRecommendationPrompt(genre=genre)))


while True:
    genre = input("Enter genre: ")
    if genre == "quit":
        break
    print(recommend_movies(genre))
