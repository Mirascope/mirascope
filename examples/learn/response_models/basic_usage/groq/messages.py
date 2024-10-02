from typing import cast

from mirascope.core import Messages, groq
from pydantic import BaseModel


class Book(BaseModel):
    """An extracted book."""

    title: str
    author: str


@groq.call("llama-3.1-70b-versatile", response_model=Book)
def extract_book(text: str) -> Messages.Type:
    return Messages.User(f"Extract {text}")


book = extract_book("The Name of the Wind by Patrick Rothfuss")
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'

response = cast(groq.GroqCallResponse, book._response)  # pyright: ignore[reportAttributeAccessIssue]
print(response.model_dump())
# > {'metadata': {}, 'response': {'id': ...}, ...}
