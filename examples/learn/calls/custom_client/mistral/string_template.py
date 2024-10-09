from mirascope.core import mistral, prompt_template
from mistralai import Mistral


@mistral.call(
    "mistral-large-latest",
    client=Mistral(api_key=mistral.load_api_key()),
)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


@mistral.call(
    "mistral-large-latest",
    client=Mistral(api_key=mistral.load_api_key()),
)
@prompt_template("Recommend a {genre} book")
async def recommend_book_async(genre: str): ...
