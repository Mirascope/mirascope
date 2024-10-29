from mirascope.core import openai, prompt_template
from openai import AsyncOpenAI


@openai.call("gpt-4o-mini", client=AsyncOpenAI())
@prompt_template("Recommend a {genre} book")
async def recommend_book_async(genre: str): ...
