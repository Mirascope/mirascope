from mirascope.core import xai
from openai import AsyncOpenAI


@xai.call(
    "grok-3-mini",
    client=AsyncOpenAI(base_url="https://api.xai.com/v1", api_key="YOUR_API_KEY"),
)
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
