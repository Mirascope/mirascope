from mirascope.core import BaseMessageParam, xai
from openai import OpenAI


@xai.call("grok-3")
def recommend_book(genre: str) -> xai.XAIDynamicConfig:
    return {
        "messages": [
            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
        ],
        "client": OpenAI(base_url="https://api.x.ai/v1"),
    }
