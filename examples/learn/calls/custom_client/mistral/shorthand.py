from mirascope.core import mistral
from mistralai.client import MistralClient


@mistral.call("mistral-large-latest", client=MistralClient())
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
