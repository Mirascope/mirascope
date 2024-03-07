"""An async script for extracting the title of a book and author given some string.
"""
import asyncio
import os

from pydantic import BaseModel

from mirascope.openai import OpenAIPrompt

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class BookInfo(BaseModel):
    """A model for book info."""

    title: str
    author: str


class BookInfoPrompt(OpenAIPrompt):
    """The Name of the Wind is by Patrick Rothfuss."""


async def extract_book_info():
    """Asynchronously extracts book info."""
    return await BookInfoPrompt().async_extract(BookInfo, retries=5)


print(asyncio.run(extract_book_info()))
