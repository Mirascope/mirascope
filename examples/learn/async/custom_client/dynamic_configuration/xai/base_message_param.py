from mirascope.core import BaseMessageParam, xai
from openai import AsyncOpenAI


@xai.call("grok-3-mini")
async def recommend_book(genre: str) -> xai.AsyncXAIDynamicConfig:
    return {
        "messages": [
            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
        ],
        "client": AsyncOpenAI(),
    }
