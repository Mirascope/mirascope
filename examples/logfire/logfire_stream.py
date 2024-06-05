import logfire

from mirascope.logfire import with_logfire
from mirascope.openai import OpenAICall

logfire.configure()


@with_logfire
class BookRecommender(OpenAICall):
    prompt_template = "Please recommend some {genre} books"

    genre: str


recommender = BookRecommender(genre="fantasy")
stream = recommender.stream()  # this will automatically get logged with logfire
for chunk in stream:
    print(chunk.content, end="", flush=True)
