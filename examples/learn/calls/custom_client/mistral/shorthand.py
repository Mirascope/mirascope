import os

from mirascope.core import mistral
from mistralai import Mistral


@mistral.call(
    "mistral-large-latest",
    client=Mistral(api_key=os.environ.get("MISTRAL_API_KEY", "")),
)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
