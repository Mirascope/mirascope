import logfire
from openai import Client

from mirascope.core import openai, prompt_template

client = Client()
logfire.configure()
logfire.instrument_openai(client)


@openai.call(model="gpt-4o-mini", client=client)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book."


recommend_book("fantasy")
