from mirascope import llm, prompt_template
from openai import AsyncOpenAI


@llm.call(provider="openai", model="gpt-4o-mini", client=AsyncOpenAI())
@prompt_template("Recommend a {genre} book")
async def recommend_book_async(genre: str): ...
