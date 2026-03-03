import os

from mirascope.core import mistral
from mistralai import Mistral # [!code highlight]


@mistral.call(
    "mistral-large-latest",
    client=Mistral(api_key=os.environ["MISTRAL_API_KEY"]), # [!code highlight]
)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
