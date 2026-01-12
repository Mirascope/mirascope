from mirascope.core import openai
from openai import OpenAI # [!code highlight]


@openai.call("gpt-4o-mini", client=OpenAI()) # [!code highlight]
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
