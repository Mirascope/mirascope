from mirascope.core import Messages, xai
from openai import OpenAI


@xai.call("grok-3", client=OpenAI(base_url="https://api.x.ai/v1"))
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")
