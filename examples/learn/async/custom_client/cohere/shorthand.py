from cohere import AsyncClient
from mirascope.core import cohere


@cohere.call("command-r-plus", client=AsyncClient())
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
