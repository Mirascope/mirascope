from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from mirascope.core import anthropic, prompt_template


class Book(BaseModel):
    title: str
    author: str


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
@anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


book = recommend_book("fantasy")
print(book)
