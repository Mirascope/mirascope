"""
Basic example using an OpenAICall to make an async call
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
    response = await BookRecommender(genre="fantasy").call_async()
    return response.content


print(asyncio.run(book_recommendation()))
# > The Name of the Wind by Patrick Rothfuss
