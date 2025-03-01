from mirascope import llm, prompt_template
from openai import AsyncOpenAI


@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
async def recommend_book(genre: str) -> openai.AsyncOpenAIDynamicConfig:
    return {
        "client": AsyncOpenAI(),
    }
