from mirascope import llm
from pydantic import BaseModel


@llm.call("vllm", "llama3.2")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


recommendation = recommend_book("fantasy")
print(recommendation)
# Output: Here are some popular and highly-recommended fantasy books...


class Book(BaseModel):
    title: str
    author: str


@llm.call("vllm", "llama3.2", response_model=Book)
def extract_book(text: str) -> str:
    return f"Extract {text}"


book = extract_book("The Name of the Wind by Patrick Rothfuss")
assert isinstance(book, Book)
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'
