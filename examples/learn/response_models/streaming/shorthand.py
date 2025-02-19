from mirascope import llm
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str


@llm.call(provider="openai", model="gpt-4o-mini", response_model=Book, stream=True)
def extract_book(text: str) -> str:
    return f"Extract {text}"


book_stream = extract_book("The Name of the Wind by Patrick Rothfuss")
for partial_book in book_stream:
    print(partial_book)
# Output:
# title=None author=None
# title='' author=None
# title='The' author=None
# title='The Name' author=None
# title='The Name of' author=None
# title='The Name of the' author=None
# title='The Name of the Wind' author=None
# title='The Name of the Wind' author=''
# title='The Name of the Wind' author='Patrick'
# title='The Name of the Wind' author='Patrick Roth'
# title='The Name of the Wind' author='Patrick Rothf'
# title='The Name of the Wind' author='Patrick Rothfuss'
