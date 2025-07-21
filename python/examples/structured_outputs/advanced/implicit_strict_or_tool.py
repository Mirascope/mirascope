from pydantic import BaseModel

from mirascope import llm


# Since we don't decorate Book with `@llm.format`, it will use "strict-or-tool" mode
class Book(BaseModel):
    title: str
    author: str
    themes: list[str]


@llm.call("openai:gpt-4o-mini", format=Book)
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


def main():
    response: llm.Response[Book] = recommend_book("fantasy")
    book: Book = response.format()

    print(f"Title: {book.title}")
    print(f"Author: {book.author}")
    print(f"Themes: {book.themes}")


if __name__ == "__main__":
    main()
