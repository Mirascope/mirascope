from mirascope.core import BaseMessageParam, xai
from openai import AsyncOpenAI


@xai.call(
    "grok-3-mini",
    client=AsyncOpenAI(base_url="https://api.xai.com/v1", api_key="YOUR_API_KEY"),
)
async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
