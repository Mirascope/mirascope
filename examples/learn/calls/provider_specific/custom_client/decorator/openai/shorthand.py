from mirascope.core import openai
from openai import OpenAI


@openai.call("gpt-4o-mini", client=OpenAI())
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
