from cohere import Client
from mirascope.core import cohere


@cohere.call("command-r-plus", client=Client())
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
