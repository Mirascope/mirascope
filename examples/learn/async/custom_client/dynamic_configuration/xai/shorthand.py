from mirascope.core import Messages, xai
from openai import AsyncOpenAI


@xai.call("grok-3-mini")
async def recommend_book(genre: str) -> xai.AsyncXAIDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": AsyncOpenAI(),
    }
