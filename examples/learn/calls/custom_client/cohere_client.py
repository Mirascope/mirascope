from cohere import AsyncClient, Client
from mirascope.core import cohere


@cohere.call("command-r-plus", client=Client())
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


@cohere.call("command-r-plus", client=AsyncClient())
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
