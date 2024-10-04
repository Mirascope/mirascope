from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from mirascope.core import anthropic


class Book(BaseModel):
    title: str
    author: str


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
@anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book."


book = recommend_book("fantasy")
print(book)
