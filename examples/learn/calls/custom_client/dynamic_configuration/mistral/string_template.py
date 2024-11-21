import os

from mirascope.core import mistral, prompt_template
from mistralai import Mistral


@mistral.call("mistral-large-latest")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str) -> mistral.MistralDynamicConfig:
    return {
        "client": Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
    }
