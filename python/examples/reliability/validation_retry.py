from pydantic import BaseModel, ValidationError

from mirascope import llm


class Book(BaseModel):
    title: str
    author: str
    year: int


@llm.call("openai/gpt-4o-mini", format=Book)
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


max_retries = 3
response = recommend_book("fantasy")
for attempt in range(max_retries):
    try:
        book = response.parse()
        print(f"{book.title} by {book.author} ({book.year})")
        break
    except ValidationError as e:
        if attempt == max_retries - 1:
            raise
        # Tell the model what went wrong so it can fix it
        response = response.resume(
            f"Your response failed validation:\n{e}\n\nPlease fix."
        )
