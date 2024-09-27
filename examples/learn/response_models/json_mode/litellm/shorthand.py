from mirascope.core import litellm
from pydantic import BaseModel


class Book(BaseModel):
    """An extracted book."""

    title: str
    author: str


@litellm.call("gpt-4o-mini", response_model=Book, json_mode=True)
def extract_book(text: str) -> str:
    return f"Extract {text}"


book = extract_book("The Name of the Wind by Patrick Rothfuss")
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'
