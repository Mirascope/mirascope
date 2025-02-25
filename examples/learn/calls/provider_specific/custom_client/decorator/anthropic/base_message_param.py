from anthropic import Anthropic
from mirascope.core import BaseMessageParam, anthropic


@anthropic.call("claude-3-5-sonnet-latest", client=Anthropic())
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
