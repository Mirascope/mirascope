from mirascope.core import Messages, mistral
from mistralai import Mistral


@mistral.call(
    "mistral-large-latest",
    client=Mistral(api_key=mistral.load_api_key()),
)
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


@mistral.call(
    "mistral-large-latest",
    client=Mistral(api_key=mistral.load_api_key()),
)
async def recommend_book_async(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")
