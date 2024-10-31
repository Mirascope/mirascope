from cohere import AsyncClient
from mirascope.core import cohere, Messages


@cohere.call("command-r-plus")
async def recommend_book(genre: str) -> cohere.AsyncCohereDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": AsyncClient(),
    }
