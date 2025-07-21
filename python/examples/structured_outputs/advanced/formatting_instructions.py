import json

from pydantic import BaseModel, Field

from mirascope import llm


@llm.format(mode="json")
class Book(BaseModel):
    title: str
    author: str
    rating: int = Field(..., description="Integer between 1 and 5 (inclusive)")

    @classmethod
    def formatting_instructions(cls) -> str:
        return f"""
        For your final response, output ONLY a valid JSON dict (NOT THE SCHEMA).
        It must adhere to this schema:
        {json.dumps(cls.model_json_schema(), indent=2)}
        """


@llm.call("openai:gpt-4o-mini", format=Book)
def recommend_book(genre: str):
    return f"Recommend a {genre} book that is available in the library."


def main():
    response: llm.Response[None, Book] = recommend_book("fantasy")
    book: Book = response.format()

    print(f"Title: {book.title}")
    print(f"Author: {book.author}")
    print(f"Rating: {book.rating}")


if __name__ == "__main__":
    main()
