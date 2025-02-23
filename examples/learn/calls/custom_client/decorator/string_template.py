from mirascope import llm, prompt_template
from openai import OpenAI


@llm.call(provider="openai", model="gpt-4o-mini", client=OpenAI())
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...
