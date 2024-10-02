from cohere import Client
from mirascope.core import BaseMessageParam, cohere


@cohere.call("command-r-plus", client=Client())
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
