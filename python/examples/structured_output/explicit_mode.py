from pydantic import BaseModel

from mirascope import llm


class Book(BaseModel):
    title: str
    author: str


@llm.call("openai/gpt-5-mini", format=llm.format(Book, mode="strict"))
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


response = recommend_book("fantasy")
book = response.parse()
print(f"{book.title} by {book.author}")
