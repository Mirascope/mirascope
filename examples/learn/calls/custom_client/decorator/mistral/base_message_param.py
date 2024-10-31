from mirascope.core import BaseMessageParam, mistral
from mistralai.client import MistralClient


@mistral.call("mistral-large-latest", client=MistralClient())
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
