from cohere import AsyncClient # [!code highlight]
from mirascope.core import cohere


@cohere.call("command-r-plus", client=AsyncClient()) # [!code highlight]
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
