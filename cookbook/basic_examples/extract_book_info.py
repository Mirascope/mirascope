"""An example script for extracting the title of a book and author given some string."""
import os

from pydantic import BaseModel

from mirascope import OpenAIChat

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class BookInfo(BaseModel):
    """A model for book info."""

    title: str
    author: str


chat = OpenAIChat(model="gpt-3.5-turbo-1106")
book_info = chat.extract(
    BookInfo,
    "The Name of the Wind is by Patrick Rothfuss.",
    retries=5,
)
print(book_info)
