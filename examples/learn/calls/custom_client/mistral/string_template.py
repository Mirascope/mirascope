from mirascope.core import mistral, prompt_template
from mistralai.async_client import MistralAsyncClient
from mistralai.client import MistralClient


@mistral.call("mistral-large-latest", client=MistralClient())
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


@mistral.call("mistral-large-latest", client=MistralAsyncClient())
@prompt_template("Recommend a {genre} book")
async def recommend_book_async(genre: str): ...
