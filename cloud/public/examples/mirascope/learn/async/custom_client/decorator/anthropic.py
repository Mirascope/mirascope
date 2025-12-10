from anthropic import AsyncAnthropic # [!code highlight]
from mirascope.core import anthropic


@anthropic.call("claude-3-5-sonnet-20240620", client=AsyncAnthropic()) # [!code highlight]
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
