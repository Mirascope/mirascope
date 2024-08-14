from pydantic import BaseModel

from mirascope.core import openai, prompt_template


class Book(BaseModel):
    title: str
    author: str


@openai.call(model="gpt-4o-mini", response_model=Book, stream=True)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


book_stream = recommend_book("science fiction")
for partial_book in book_stream:
    print(partial_book)
