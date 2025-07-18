from dataclasses import dataclass

from mirascope import llm


@dataclass
class Book:
    title: str
    author: str


@llm.call("openai:gpt-4o-mini", format=Book)
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


def main():
    stream: llm.Stream[None, Book] = recommend_book.stream("fantasy")
    for _ in stream:
        partial_book: Book = stream.format()
        print(partial_book)


main()
