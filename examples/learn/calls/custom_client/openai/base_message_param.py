from mirascope.core import BaseMessageParam, openai
from openai import OpenAI


@openai.call("gpt-4o-mini", client=OpenAI())
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
