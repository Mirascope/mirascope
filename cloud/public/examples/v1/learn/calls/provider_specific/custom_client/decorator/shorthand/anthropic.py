from anthropic import Anthropic # [!code highlight]
from mirascope.core import anthropic


@anthropic.call("claude-3-5-sonnet-latest", client=Anthropic()) # [!code highlight]
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
