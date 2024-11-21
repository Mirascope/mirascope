import os

from mirascope.core import BaseMessageParam, mistral
from mistralai import Mistral


@mistral.call("mistral-large-latest")
def recommend_book(genre: str) -> mistral.MistralDynamicConfig:
    return {
        "messages": [
            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
        ],
        "client": Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
    }
