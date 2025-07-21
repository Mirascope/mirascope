from pydantic import BaseModel

from mirascope import llm


# Under the hood, will construct an ad-hoc response format tool (not revealed in recommend_book.toolkit)
@llm.format(mode="tool")
class Book(BaseModel):
    title: str
    author: str
    themes: list[str]


@llm.call("openai:gpt-4o-mini", format=Book)
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


def main():
    response: llm.Response[None, Book] = recommend_book("fantasy")
    # Model returns a tool call, but we translate it into text content
    assert response.tool_call is None
    book: Book = response.format()

    print(f"Title: {book.title}")
    print(f"Author: {book.author}")
    print(f"Themes: {book.themes}")


if __name__ == "__main__":
    main()
