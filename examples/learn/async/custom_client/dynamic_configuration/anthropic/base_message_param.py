from anthropic import AsyncAnthropic
from mirascope.core import BaseMessageParam, anthropic


@anthropic.call("claude-3-5-sonnet-20240620")
async def recommend_book(genre: str) -> anthropic.AsyncAnthropicDynamicConfig:
    return {
        "messages": [
            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
        ],
        "client": AsyncAnthropic(),
    }
