from groq import AsyncGroq
from mirascope.core import groq, prompt_template


@groq.call("llama-3.3-70b-versatile")
@prompt_template("Recommend a {genre} book")
async def recommend_book(genre: str) -> groq.AsyncGroqDynamicConfig:
    return {
        "client": AsyncGroq(),
    }
