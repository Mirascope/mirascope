import os

from mirascope.core import Messages, mistral
from mistralai import Mistral


@mistral.call(
    "mistral-large-latest", client=Mistral(api_key=os.environ["MISTRAL_API_KEY"])
)
async def recommend_book_async(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")
