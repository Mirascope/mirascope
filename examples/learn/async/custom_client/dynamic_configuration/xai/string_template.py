from mirascope.core import prompt_template, xai
from openai import AsyncOpenAI


@xai.call("grok-3-mini")
@prompt_template("Recommend a {genre} book")
async def recommend_book(genre: str) -> xai.AsyncXAIDynamicConfig:
    return {
        "client": AsyncOpenAI(),
    }
