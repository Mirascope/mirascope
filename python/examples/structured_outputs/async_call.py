import asyncio
from dataclasses import dataclass

from mirascope import llm


@dataclass
class Book:
    title: str
    author: str


@llm.call("openai:gpt-4o-mini", format=Book)
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


async def main():
    response: llm.Response[None, Book] = await recommend_book.call_async("fantasy")
    book: Book = response.format()
    print(book)


asyncio.run(main())
