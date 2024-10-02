from cohere import AsyncClient
from mirascope.core import BaseMessageParam, cohere


@cohere.call("command-r-plus", client=AsyncClient())
async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
