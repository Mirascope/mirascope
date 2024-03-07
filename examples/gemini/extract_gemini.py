from google.generativeai import configure  # type: ignore
from pydantic import BaseModel

from mirascope.gemini import GeminiPrompt

configure(api_key="YOUR_GEMINI_API_KEY")


class BookInfo(BaseModel):
    """A model for book info."""

    title: str
    author: str


class BookPrompt(GeminiPrompt):
    """The book title is 'The Name of the Wind' and the author is Patrick Rothfuss."""


print(BookPrompt().extract(BookInfo, retries=5))
