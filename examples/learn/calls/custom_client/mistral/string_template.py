from mirascope.core import mistral, prompt_template
from mistralai.client import MistralClient


@mistral.call("mistral-large-latest", client=MistralClient())
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...
