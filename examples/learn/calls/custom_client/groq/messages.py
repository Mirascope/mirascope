from groq import AsyncGroq, Groq
from mirascope.core import Messages, groq


@groq.call("llama-3.1-8b-instant", client=Groq())
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


@groq.call("llama-3.1-8b-instant", client=AsyncGroq())
async def recommend_book_async(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")
