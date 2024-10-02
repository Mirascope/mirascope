from mirascope.core import Messages, mistral
from mistralai.client import MistralClient


@mistral.call("mistral-large-latest", client=MistralClient())
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")
