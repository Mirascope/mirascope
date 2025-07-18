from typing import Annotated

from pydantic import BaseModel

from mirascope import llm


class Book(BaseModel):
    # title and summary will be auto-populated from the call args
    title: Annotated[str, llm.formatting.FromCallArgs()]
    author: Annotated[str, llm.formatting.FromCallArgs()]
    summary: str


@llm.call("openai:gpt-4o-mini", format=Book)
def summarize_book(title: str, author: str):
    return f"Summarize {title} by {author}."


def main():
    response: llm.Response[None, Book] = summarize_book(
        "The Name of the Wind", "Patrick Rothfuss"
    )
    book: Book = response.format()
    print(book)


main()
