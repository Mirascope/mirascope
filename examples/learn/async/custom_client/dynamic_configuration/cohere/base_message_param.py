from cohere import AsyncClient
from mirascope.core import BaseMessageParam, cohere


@cohere.call("command-r-plus")
async def recommend_book(genre: str) -> cohere.AsyncCohereDynamicConfig:
    return {
        "messages": [
            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
        ],
        "client": AsyncClient(),
    }
