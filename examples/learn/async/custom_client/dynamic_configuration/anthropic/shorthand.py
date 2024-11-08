from anthropic import AsyncAnthropic
from mirascope.core import anthropic, Messages


@anthropic.call("claude-3-5-sonnet-20240620")
async def recommend_book(genre: str) -> anthropic.AsyncAnthropicDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": AsyncAnthropic(),
    }
