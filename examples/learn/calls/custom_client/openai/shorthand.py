from mirascope.core import openai
from openai import AsyncOpenAI, OpenAI


@openai.call("gpt-4o-mini", client=OpenAI())
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


@openai.call("gpt-4o-mini", client=AsyncOpenAI())
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
