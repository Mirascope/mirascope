from anthropic import Anthropic
from mirascope.core import anthropic


@anthropic.call("claude-3-5-sonnet-20240620", client=Anthropic())
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
