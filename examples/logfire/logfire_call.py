import logfire
from dotenv import find_dotenv, load_dotenv

from mirascope.cohere import CohereCall
from mirascope.logfire import with_logfire

logfire.configure()
load_dotenv(find_dotenv())


@with_logfire
class BookRecommender(CohereCall):
    prompt_template = "Please recommend some {genre} books"

    genre: str


recommender = BookRecommender(genre="fantasy")
response = recommender.call()  # this will automatically get logged with logfire
print(response.content)
