from groq import AsyncGroq # [!code highlight]
from mirascope.core import groq, prompt_template


@groq.call("llama-3.1-70b-versatile", client=AsyncGroq()) # [!code highlight]
@prompt_template("Recommend a {genre} book")
async def recommend_book_async(genre: str): ...
