from mirascope.core import bedrock, prompt_template
from pydantic import BaseModel


class Book(BaseModel):
    """An extracted book."""

    title: str
    author: str


@bedrock.call(
    "anthropic.claude-3-haiku-20240307-v1:0", response_model=Book, json_mode=True
)
@prompt_template("Extract {text}")
def extract_book(text: str): ...


book = extract_book("The Name of the Wind by Patrick Rothfuss")
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'
