from anthropic import AsyncAnthropic
from mirascope.core import Messages, anthropic


@anthropic.call("claude-3-5-sonnet-20240620", client=AsyncAnthropic())
async def recommend_book_async(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")
