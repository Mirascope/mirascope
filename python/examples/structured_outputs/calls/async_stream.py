import asyncio
import contextlib

from pydantic import BaseModel

from mirascope import llm


class Book(BaseModel):
    title: str
    author: str
    themes: list[str]


@llm.call("openai:gpt-4o-mini", format=Book)
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


async def main():
    stream: llm.AsyncStream[None, Book] = await recommend_book.stream_async("fantasy")
    async for _ in stream:
        partial_book: Book | None = None
        with contextlib.suppress(Exception):
            partial_book = stream.format()
        if partial_book is not None:
            print("Partial book: ", partial_book)

    book: Book = stream.format()
    print("Book: ", book)


asyncio.run(main())
