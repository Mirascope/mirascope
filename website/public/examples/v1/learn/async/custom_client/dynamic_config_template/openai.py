from mirascope.core import openai, prompt_template
from openai import AsyncOpenAI # [!code highlight]


@openai.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
async def recommend_book(genre: str) -> openai.AsyncOpenAIDynamicConfig:
    return {
        "client": AsyncOpenAI(), # [!code highlight]
    }
