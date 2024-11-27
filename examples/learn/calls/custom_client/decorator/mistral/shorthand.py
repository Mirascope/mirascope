import os

from mirascope.core import mistral
from mistralai import Mistral


@mistral.call(
    "mistral-large-latest",
    client=Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


@mistral.call(
    "mistral-large-latest",
    client=Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
)
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
