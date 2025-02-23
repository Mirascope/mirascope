from mirascope import llm
from openai import OpenAI


@llm.call(provider="openai", model="gpt-4o-mini", client=OpenAI())
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
