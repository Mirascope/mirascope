from mirascope import Messages, llm
from openai import AsyncOpenAI


@llm.call(provider="openai", model="gpt-4o-mini", client=AsyncOpenAI())
async def recommend_book_async(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")
