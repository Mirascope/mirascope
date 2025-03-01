from mirascope import BaseMessageParam, llm
from openai import AsyncOpenAI


@llm.call(provider="openai", model="gpt-4o-mini")
async def recommend_book(genre: str) -> openai.AsyncOpenAIDynamicConfig:
    return {
        "messages": [
            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
        ],
        "client": AsyncOpenAI(),
    }
