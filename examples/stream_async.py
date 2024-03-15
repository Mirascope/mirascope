"""
Basic example using an OpenAICall to async stream an async call
"""
import asyncio
import os

from mirascope.openai import OpenAICall

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class BookRecommender(OpenAICall):
    prompt_template = "Please recommend a {genre} book."

    genre: str


async def book_recommendation():
    """Asynchronously creates the response for a chat completion."""
    stream = await BookRecommender(genre="fantasy").stream_async()
    async for chunk in stream:
        print(chunk, end="")


asyncio.run(book_recommendation())
# > The Name of the Wind by Patrick Rothfuss
