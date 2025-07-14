import asyncio
from dataclasses import dataclass

from mirascope import llm


@dataclass
class Library:
    available_books: list[str]


@dataclass
class Book:
    title: str
    author: str


@llm.call("openai:gpt-4o-mini", response_format=Book, deps_type=Library)
def recommend_book(ctx: llm.Context[Library], genre: str):
    return f"""
    Recommend a {genre} book.
    The following books are available: {ctx.deps.available_books}
    """


async def main():
    library = Library(available_books=["Mistborn", "Dune", "The Name of the Wind"])
    with llm.context(deps=library) as ctx:
        stream: llm.AsyncStream[Library, Book] = recommend_book.stream_async(
            ctx, "fantasy"
        )
        async for _ in stream:
            partial_book: Book = stream.format()
            print(partial_book)


asyncio.run(main())
