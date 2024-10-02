from mirascope.core import Messages, openai
from openai import AsyncOpenAI


@openai.call("gpt-4o-mini", client=AsyncOpenAI())
async def recommend_book_async(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")
