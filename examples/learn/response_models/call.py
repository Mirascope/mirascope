from pydantic import BaseModel

from mirascope.core import openai, prompt_template


class Book(BaseModel):
    title: str
    author: str


@openai.call(model="gpt-4o-mini", response_model=Book)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


book = recommend_book("science fiction")
assert isinstance(book, Book)
print(f"Title: {book.title}")
print(f"Author: {book.author}")
