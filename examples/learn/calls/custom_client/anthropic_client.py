from anthropic import Anthropic, AsyncAnthropic
from mirascope.core import anthropic


@anthropic.call("claude-3-5-sonnet-20240620", client=Anthropic())
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


@anthropic.call("claude-3-5-sonnet-20240620", client=AsyncAnthropic())
async def recommend_book_async(genre: str) -> str:
    return f"Recommend a {genre} book"
