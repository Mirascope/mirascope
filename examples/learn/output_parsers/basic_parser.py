from pydantic import BaseModel

from mirascope.core import anthropic, prompt_template


class Book(BaseModel):
    title: str
    author: str


def parse_book_recommendation(response: anthropic.AnthropicCallResponse) -> Book:
    title, author = response.content.split(" by ")
    return Book(title=title, author=author)


@anthropic.call(
    model="claude-3-5-sonnet-20240620", output_parser=parse_book_recommendation
)
@prompt_template("Recommend a {genre} book in the format Title by Author")
def recommend_book(genre: str): ...


book = recommend_book("science fiction")
print(f"Title: {book.title}")
print(f"Author: {book.author}")
