from groq import AsyncGroq
from mirascope.core import groq, prompt_template


@groq.call("llama-3.1-8b-instant", client=AsyncGroq())
@prompt_template("Recommend a {genre} book")
async def recommend_book_async(genre: str): ...
