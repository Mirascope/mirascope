import asyncio
from dataclasses import dataclass

from mirascope import llm


@dataclass
class Book:
    title: str
    author: str


@llm.call("openai:gpt-4o-mini", response_format=Book)
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


async def main():
    stream: llm.AsyncStream[None, Book] = await recommend_book.stream_async("fantasy")
    async for _ in stream:
        partial_book: Book = stream.format()
        print(partial_book)


asyncio.run(main())
