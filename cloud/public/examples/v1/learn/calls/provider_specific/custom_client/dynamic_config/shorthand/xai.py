from mirascope.core import Messages, xai
from openai import OpenAI # [!code highlight]


@xai.call("grok-3")
def recommend_book(genre: str) -> xai.XAIDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "client": OpenAI(base_url="https://api.x.ai/v1"), # [!code highlight]
    }
