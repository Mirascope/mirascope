from mirascope.core import prompt_template, xai
from openai import OpenAI # [!code highlight]


@xai.call("grok-3")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str) -> xai.XAIDynamicConfig:
    return {
        "client": OpenAI(base_url="https://api.x.ai/v1"), # [!code highlight]
    }
