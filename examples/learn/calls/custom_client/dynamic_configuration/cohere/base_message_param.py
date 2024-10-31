from cohere import Client
from mirascope.core import BaseMessageParam, cohere


@cohere.call("command-r-plus")
def recommend_book(genre: str) -> cohere.CohereDynamicConfig:
    return {
        "messages": [
            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
        ],
        "client": Client(),
    }
