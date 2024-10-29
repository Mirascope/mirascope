from mirascope.core import BaseMessageParam, openai
from openai import OpenAI


@openai.call("gpt-4o-mini")
def recommend_book(genre: str) -> openai.OpenAIDynamicConfig:
    return {
        "messages": [
            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
        ],
        "client": OpenAI(),
    }
