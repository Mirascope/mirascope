from mirascope.core import openai, Messages
from openai import OpenAI


@openai.call("gpt-4o-mini")
def recommend_book(genre: str) -> openai.OpenAIDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": OpenAI(),
    }
