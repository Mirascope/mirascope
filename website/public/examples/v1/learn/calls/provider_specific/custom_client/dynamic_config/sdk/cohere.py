from cohere import Client
from mirascope.core import cohere, Messages


@cohere.call("command-r-plus")
def recommend_book(genre: str) -> cohere.CohereDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": Client(),
    }
