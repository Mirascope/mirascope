from mirascope.core import prompt_template, xai
from openai import AsyncOpenAI


@xai.call(
    "grok-3-mini",
    client=AsyncOpenAI(base_url="https://api.xai.com/v1", api_key="YOUR_API_KEY"),
)
@prompt_template("Recommend a {genre} book")
async def recommend_book_async(genre: str): ...
