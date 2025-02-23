from mirascope import Messages, llm
from openai import OpenAI


@llm.call(provider="openai", model="gpt-4o-mini", client=OpenAI())
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")
