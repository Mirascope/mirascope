from mirascope.core import mistral, prompt_template
from mistralai import Mistral


@mistral.call("mistral-large-latest", client=Mistral())
@prompt_template("Recommend a {genre} book")
async def recommend_book_async(genre: str): ...
