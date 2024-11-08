from mirascope.core import mistral, prompt_template
from mistralai.async_client import MistralAsyncClient


@mistral.call("mistral-large-latest", client=MistralAsyncClient())
@prompt_template("Recommend a {genre} book")
async def recommend_book_async(genre: str): ...
