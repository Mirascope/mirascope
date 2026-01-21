from pydantic import BaseModel

from mirascope import llm


class Book(BaseModel):
    title: str
    author: str


def recommend_book(genre: str) -> llm.Response[Book]:
    model: llm.Model = llm.use_model("openai/gpt-5")
    return model.call(
        f"Please recommend a book in {genre}.",
        format=Book,  # [!code highlight]
    )


def main():
    response: llm.Response[Book] = recommend_book("fantasy")
    book: Book = response.parse()
    print(f"{book.title} by {book.author}")


main()
