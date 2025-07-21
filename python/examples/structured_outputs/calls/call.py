from pydantic import BaseModel

from mirascope import llm


class Book(BaseModel):
    title: str
    author: str


@llm.call("openai:gpt-4o-mini", format=Book)
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


def main():
    response: llm.Response[None, Book] = recommend_book("fantasy")
    book: Book = response.format()
    print(book)


main()
