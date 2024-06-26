"""This example shows how to use logfire to log Mirascope calls."""
import logfire

from mirascope.logfire import with_logfire
from mirascope.openai import OpenAICall

logfire.configure()


@with_logfire
class BookRecommender(OpenAICall):
    prompt_template = "Please recommend some {genre} books"

    genre: str


recommender = BookRecommender(genre="fantasy")
response = recommender.call()  # this will automatically get logged with logfire
print(response.content)
