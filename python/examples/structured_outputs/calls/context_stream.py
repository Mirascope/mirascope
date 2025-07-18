import contextlib
from dataclasses import dataclass

from pydantic import BaseModel

from mirascope import llm


@dataclass
class Library:
    available_books: list[str]


class Book(BaseModel):
    title: str
    author: str
    themes: list[str]


@llm.call("openai:gpt-4o-mini", format=Book, deps_type=Library)
def recommend_book(ctx: llm.Context[Library], genre: str):
    return f"""
    Recommend a {genre} book.
    The following books are available: {ctx.deps.available_books}
    """


def main():
    library = Library(available_books=["Mistborn", "Dune", "The Name of the Wind"])
    ctx = llm.Context(deps=library)
    stream: llm.Stream[Library, Book] = recommend_book.stream(ctx, "fantasy")
    for _ in stream:
        partial_book: Book | None = None
        with contextlib.suppress(Exception):
            partial_book = stream.format()
        if partial_book is not None:
            print("Partial book: ", partial_book)

    book: Book = stream.format()
    print("Book: ", book)


main()
