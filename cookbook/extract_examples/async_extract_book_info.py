"""An example script for extracting the title of a book and author given some string 
asynchronously.
"""
import asyncio
import os

from pydantic import BaseModel

from mirascope import AsyncOpenAIChat

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class BookInfo(BaseModel):
    """A model for book info."""

    title: str
    author: str


async def extract_book_info():
    """Asynchronously extracts book info."""
    chat = AsyncOpenAIChat(model="gpt-3.5-turbo-1106")
    return await chat.extract(
        BookInfo,
        "The Name of the Wind is by Patrick Rothfuss.",
        retries=5,
    )


print(asyncio.run(extract_book_info()))
