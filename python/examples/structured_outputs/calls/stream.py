from pydantic import BaseModel

from mirascope import llm


class Book(BaseModel):
    title: str
    author: str
    themes: list[str]


@llm.call("openai:gpt-4o-mini", format=Book)
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


def main():
    stream: llm.Stream[Book] = recommend_book.stream("fantasy")
    for _ in stream:
        partial_book: llm.Partial[Book] = stream.format(partial=True)
        print("Partial book: ", partial_book)

    book: Book = stream.format()
    print("Book: ", book)


main()
