from groq import AsyncGroq, Groq
from mirascope.core import groq, prompt_template


@groq.call("llama-3.1-8b-instant", client=Groq())
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


@groq.call("llama-3.1-8b-instant", client=AsyncGroq())
@prompt_template("Recommend a {genre} book")
async def recommend_book_async(genre: str): ...
