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
    response: llm.Response[Book] = recommend_book(ctx, "fantasy")
    book: Book = response.format()
    print(book)


main()
