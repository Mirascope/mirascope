from pydantic import BaseModel

from mirascope import llm


class Book(BaseModel):
    title: str
    author: str
    summary: str


@llm.call("openai/gpt-5-mini", format=Book)
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


response = recommend_book.stream("fantasy")

# Stream partial objects as fields are populated
for partial in response.structured_stream():
    # partial is a Partial[Book] with all fields optional
    print(f"Partial: {partial}")

# Get the final validated object
book = response.parse()
print(f"\nFinal: {book.title} by {book.author}")
