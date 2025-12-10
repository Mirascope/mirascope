import os

from mirascope.core import mistral, prompt_template
from mistralai import Mistral # [!code highlight]


@mistral.call(
    "mistral-large-latest", client=Mistral(api_key=os.environ["MISTRAL_API_KEY"]) # [!code highlight]
)
@prompt_template("Recommend a {genre} book")
async def recommend_book_async(genre: str): ...
