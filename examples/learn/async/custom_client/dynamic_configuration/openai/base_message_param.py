from mirascope.core import BaseMessageParam, openai
from openai import AsyncOpenAI


@openai.call("gpt-4o-mini")
async def recommend_book(genre: str) -> openai.AsyncOpenAIDynamicConfig:
    return {
        "messages": [
            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
        ],
        "client": AsyncOpenAI(),
    }
