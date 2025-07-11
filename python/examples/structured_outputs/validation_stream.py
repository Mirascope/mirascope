from pydantic import BaseModel, Field, ValidationError

from mirascope import llm


class Book(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    pages: int = Field(ge=0)


@llm.call("openai:gpt-4o-mini", response_format=Book)
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


def main():
    stream: llm.Stream[None, Book] = recommend_book.stream("fantasy")

    for _ in stream:
        try:
            partial_book: Book = stream.format()
            print(partial_book)
        except ValidationError as e:
            print(f"Validation failed: {e}")


main()
