from mirascope import BaseMessageParam, llm
from openai import OpenAI


@llm.call(provider="openai", model="gpt-4o-mini", client=OpenAI())
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
