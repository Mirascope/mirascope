from mirascope.core import anthropic, prompt_template
from pydantic import BaseModel


class Book(BaseModel):
    """An extracted book."""

    title: str
    author: str


@anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
@prompt_template()
def extract_book():
    return "The Name of the Wind by Patrick Rothfuss"


book = extract_book()
assert isinstance(book, Book)
print(book)
