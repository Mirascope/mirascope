from pydantic import BaseModel, Field

from mirascope import llm


class Author(BaseModel):
    first_name: str
    last_name: str


class Book(BaseModel):
    """A book recommendation. The title should be in ALL CAPS."""

    title: str
    author: Author
    rating: int = Field(description="Rating from 1-10")


@llm.call("openai/gpt-5-mini", format=Book)
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


response = recommend_book("fantasy")
book = response.parse()
print(f"{book.title} by {book.author.first_name} {book.author.last_name}")
# THE NAME OF THE WIND by Patrick Rothfuss
print(f"Rating: {book.rating}/10")
# Rating: 9/10
