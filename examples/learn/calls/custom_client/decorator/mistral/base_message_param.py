from mirascope.core import BaseMessageParam, mistral
from mistralai import Mistral


@mistral.call(
    "mistral-large-latest",
    client=Mistral(api_key=mistral.load_api_key()),
)
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


@mistral.call(
    "mistral-large-latest",
    client=Mistral(api_key=mistral.load_api_key()),
)
async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
