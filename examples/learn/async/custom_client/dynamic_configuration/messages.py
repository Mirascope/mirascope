from mirascope import Messages, llm
from openai import AsyncOpenAI


@llm.call(provider="openai", model="gpt-4o-mini")
async def recommend_book(genre: str) -> openai.AsyncOpenAIDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": AsyncOpenAI(),
    }
