import os

from mirascope.core import BaseMessageParam, mistral
from mistralai import Mistral


@mistral.call(
    "mistral-large-latest", client=Mistral(api_key=os.environ["MISTRAL_API_KEY"])
)
async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
