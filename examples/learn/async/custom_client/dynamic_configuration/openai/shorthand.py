from mirascope.core import openai, Messages
from openai import AsyncOpenAI


@openai.call("gpt-4o-mini")
async def recommend_book(genre: str) -> openai.AsyncOpenAIDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": AsyncOpenAI(),
    }
