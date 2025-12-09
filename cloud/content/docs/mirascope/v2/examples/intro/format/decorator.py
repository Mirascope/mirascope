from pydantic import BaseModel

from mirascope import llm


class Book(BaseModel):
    title: str
    author: str


@llm.call(provider="openai", model_id="gpt-5", format=Book)
def recommend_book(genre: str):
    return f"Please recommend a book in {genre}."


def main():
    response: llm.Response[Book] = recommend_book("fantasy")
    book: Book = response.parse()
    print(f"{book.title} by {book.author}")


main()
