"""A script for figuring out extract."""
from pydantic import BaseModel

from mirascope import OpenAIChat


class BookInfo(BaseModel):
    title: str
    author: str


chat = OpenAIChat(model="gpt-3.5-turbo-1106")
book_info = chat.extract(
    "The Name of the Wind is by Patrick Rothfuss.",
    BookInfo,
    retries=5,
)
print(book_info)
