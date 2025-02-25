from anthropic import Anthropic
from mirascope.core import anthropic


@anthropic.call("claude-3-5-sonnet-latest", client=Anthropic())
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
