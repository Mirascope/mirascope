from anthropic import Anthropic
from mirascope.core import BaseMessageParam, anthropic


@anthropic.call("claude-3-5-sonnet-latest")
def recommend_book(genre: str) -> anthropic.AnthropicDynamicConfig:
    return {
        "messages": [
            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
        ],
        "client": Anthropic(),
    }
