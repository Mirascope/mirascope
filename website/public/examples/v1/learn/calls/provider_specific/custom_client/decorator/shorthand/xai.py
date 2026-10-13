from mirascope.core import xai
from openai import OpenAI # [!code highlight]


@xai.call("grok-3", client=OpenAI(base_url="https://api.x.ai/v1")) # [!code highlight]
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
