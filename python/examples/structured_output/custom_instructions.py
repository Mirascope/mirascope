from pydantic import BaseModel

from mirascope import llm


class Book(BaseModel):
    title: str
    author: str
    rating: int

    @classmethod
    def formatting_instructions(cls) -> str:
        return (
            "Output the book as JSON. "
            "The title should be in ALL CAPS. "
            "The rating should always be the number 7."
        )


@llm.call("openai/gpt-5-mini", format=Book)
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


response = recommend_book("fantasy")
book = response.parse()
print(f"{book.title} by {book.author}, rating: {book.rating}")
# THE NAME OF THE WIND by Patrick Rothfuss, rating: 7
