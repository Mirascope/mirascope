from mirascope.core import Messages, mistral
from mistralai.async_client import MistralAsyncClient


@mistral.call("mistral-large-latest", client=MistralAsyncClient())
async def recommend_book_async(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")
