"""An example script for extracting the title of a book and author given some string."""
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


book_info = BookInfoPrompt().extract(BookInfo, retries=5)
print(book_info)
