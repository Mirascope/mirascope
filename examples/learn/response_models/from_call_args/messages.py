from typing import Annotated

from mirascope import Messages, llm
from mirascope.core import FromCallArgs
from pydantic import BaseModel, model_validator
from typing_extensions import Self


class Book(BaseModel):
    title: str
    author: str


class Books(BaseModel):
    texts: Annotated[list[str], FromCallArgs()]
    books: list[Book]

    @model_validator(mode="after")
    def validate_output_length(self) -> Self:
        if len(self.texts) != len(self.books):
            raise ValueError("length mismatch...")
        return self


@llm.call(provider="openai", model="gpt-4o-mini", response_model=Books)
def extract_books(texts: list[str]) -> Messages.Type:
    return Messages.User(f"Extract the books from these texts: {texts}")


texts = [
    "The Name of the Wind by Patrick Rothfuss",
    "Mistborn: The Final Empire by Brandon Sanderson",
]
print(extract_books(texts))
# Output:
# texts=[
#     'The Name of the Wind by Patrick Rothfuss',
#     'Mistborn: The Final Empire by Brandon Sanderson'
# ]
# books=[
#     Book(title='The Name of the Wind', author='Patrick Rothfuss'),
#     Book(title='Mistborn: The Final Empire', author='Brandon Sanderson')
# ]
