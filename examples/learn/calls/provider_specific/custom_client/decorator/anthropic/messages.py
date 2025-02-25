from anthropic import Anthropic
from mirascope.core import Messages, anthropic


@anthropic.call("claude-3-5-sonnet-latest", client=Anthropic())
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")
