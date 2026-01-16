from pydantic import BaseModel

from mirascope import llm


class Book(BaseModel):
    title: str
    author: str


@llm.call("openai/gpt-4o-mini", format=list[Book])
def recommend_books(genre: str, count: int):
    return f"Recommend {count} {genre} books."


books = recommend_books("fantasy", 3).parse()
for book in books:
    print(f"{book.title} by {book.author}")
# The Name of the Wind by Patrick Rothfuss
# Mistborn: The Final Empire by Brandon Sanderson
# The Way of Kings by Brandon Sanderson
