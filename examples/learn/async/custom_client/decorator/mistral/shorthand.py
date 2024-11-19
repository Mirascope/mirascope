from mirascope.core import mistral
from mistralai import Mistral


@mistral.call("mistral-large-latest", client=Mistral())
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
