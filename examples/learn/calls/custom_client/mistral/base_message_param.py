from mirascope.core import BaseMessageParam, mistral
from mistralai.async_client import MistralAsyncClient
from mistralai.client import MistralClient


@mistral.call("mistral-large-latest", client=MistralClient())
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


@mistral.call("mistral-large-latest", client=MistralAsyncClient())
async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
