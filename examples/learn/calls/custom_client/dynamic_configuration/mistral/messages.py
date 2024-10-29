from mirascope.core import Messages, mistral
from mistralai.client import MistralClient


@mistral.call("mistral-large-latest")
def recommend_book(genre: str) -> mistral.MistralDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": MistralClient(),
    }
