import asyncio
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


@llm.context_call("openai:gpt-4o-mini", format=Book, deps_type=Library)
def recommend_book(ctx: llm.Context[Library], genre: str):
    return f"""
    Recommend a {genre} book.
    The following books are available: {ctx.deps.available_books}
    """


async def main():
    library = Library(available_books=["Mistborn", "Dune", "The Name of the Wind"])
    ctx = llm.Context(deps=library)
    stream: llm.AsyncStream[Book] = await recommend_book.stream_async(ctx, "fantasy")
    async for _ in stream:
        partial_book: llm.Partial[Book] = stream.format(partial=True)
        print("Partial book: ", partial_book)

    book: Book = stream.format()
    print("Book: ", book)


asyncio.run(main())
