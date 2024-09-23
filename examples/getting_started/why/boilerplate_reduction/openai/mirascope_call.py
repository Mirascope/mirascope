from mirascope.core import openai, prompt_template
from pydantic import BaseModel


class Book(BaseModel):
    """An extracted book."""

    title: str
    author: str


@openai.call("gpt-4o-mini", response_model=Book)
@prompt_template()
def extract_book():
    return "The Name of the Wind by Patrick Rothfuss"


book = extract_book()
assert isinstance(book, Book)
print(book)
