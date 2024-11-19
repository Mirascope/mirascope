from mirascope.core import mistral, Messages
from mistralai import Mistral


@mistral.call("mistral-large-latest")
def recommend_book(genre: str) -> mistral.MistralDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": Mistral(),
    }
