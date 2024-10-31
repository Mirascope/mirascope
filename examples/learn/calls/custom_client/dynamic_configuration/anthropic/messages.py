from anthropic import Anthropic
from mirascope.core import Messages, anthropic


@anthropic.call("claude-3-5-sonnet-20240620")
def recommend_book(genre: str) -> anthropic.AnthropicDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": Anthropic(),
    }
