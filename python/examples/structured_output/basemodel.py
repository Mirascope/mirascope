from pydantic import BaseModel

from mirascope import llm


class Book(BaseModel):
    title: str
    author: str


@llm.call("openai/gpt-4o-mini", format=Book)
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


book = recommend_book("fantasy").parse()
print(f"{book.title} by {book.author}")
# The Name of the Wind by Patrick Rothfuss
