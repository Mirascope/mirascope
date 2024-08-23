import logfire
from openai import Client

from mirascope.core import openai, prompt_template

client = Client()
logfire.configure()
logfire.instrument_openai(client)


@openai.call(model="gpt-4o-mini", client=client)
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str): ...


recommend_book("fantasy")
