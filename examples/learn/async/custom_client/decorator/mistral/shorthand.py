from mirascope.core import mistral
from mistralai.async_client import MistralAsyncClient


@mistral.call("mistral-large-latest", client=MistralAsyncClient())
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
