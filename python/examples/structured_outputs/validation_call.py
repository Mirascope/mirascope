from pydantic import BaseModel, Field, ValidationError

from mirascope import llm


class Book(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    pages: int = Field(ge=0)


@llm.call("openai:gpt-4o-mini", response_format=Book)
def recommend_book(genre: str):
    return f"Recommend a {genre} book with page count."


def main():
    response: llm.Response[None, Book] = recommend_book("fantasy")
    try:
        book: Book = response.format()
        print(book)
    except ValidationError as e:
        print(f"Validation failed: {e}")


main()
