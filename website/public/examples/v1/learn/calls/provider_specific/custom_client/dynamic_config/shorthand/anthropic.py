from anthropic import Anthropic # [!code highlight]
from mirascope.core import Messages, anthropic


@anthropic.call("claude-3-5-sonnet-latest")
def recommend_book(genre: str) -> anthropic.AnthropicDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": Anthropic(), # [!code highlight]
    }
