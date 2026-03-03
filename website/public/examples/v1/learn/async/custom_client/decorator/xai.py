from mirascope.core import xai
from openai import AsyncOpenAI # [!code highlight]


@xai.call(
    "grok-3-mini",
    client=AsyncOpenAI(base_url="https://api.xai.com/v1", api_key="YOUR_API_KEY"), # [!code highlight]
)
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
