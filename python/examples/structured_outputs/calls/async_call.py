import asyncio

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
    response: llm.Response[Book] = await recommend_book.call_async("fantasy")
    book: Book = response.format()
    print(book)


asyncio.run(main())
