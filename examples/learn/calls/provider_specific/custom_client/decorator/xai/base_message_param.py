from mirascope.core import BaseMessageParam, xai
from openai import OpenAI


@xai.call("grok-3", client=OpenAI(base_url="https://api.x.ai/v1"))
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
