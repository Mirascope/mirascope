from dataclasses import dataclass

from mirascope import llm


@llm.tool()
def in_library() -> list[str]:
    return ["Dune", "The Name of the Wind", "Mistborn"]


@llm.tool()
def lookup_isbn(book_title: str) -> str:
    isbns = {
        "Dune": "9780593099322",
        "Mistborn": "9780765360960",
        "The Way of Kings": "9780765376671",
    }
    return isbns[book_title]


@dataclass
class Book:
    title: str
    author: str
    isbn: str


@llm.call("openai:gpt-4o-mini", response_format=Book)
def recommend_book(genre: str):
    return f"Recommend a {genre} book from the library. Ensure the isbn is accurate."


def main():
    response: llm.Response[None, Book] = recommend_book("fantasy")
    while tool_call := response.tool_call:
        output = recommend_book.call_tool(tool_call)
        response = recommend_book.resume(response, output)
    # Now that we have text response, format it
    # TODO: Discuss how we want to implement response.format
    book: Book = response.format()
    print(book)


main()
