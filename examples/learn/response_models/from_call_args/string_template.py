from typing import Annotated

from mirascope import llm, prompt_template
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
@prompt_template("Extract the books from these texts: {texts}")
def extract_books(texts: list[str]): ...


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
