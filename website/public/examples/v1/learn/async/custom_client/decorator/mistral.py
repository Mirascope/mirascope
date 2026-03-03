import os

from mirascope.core import mistral
from mistralai import Mistral # [!code highlight]


@mistral.call(
    "mistral-large-latest", client=Mistral(api_key=os.environ["MISTRAL_API_KEY"]) # [!code highlight]
)
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
