from pydantic import BaseModel

from mirascope import llm


@llm.tool
def in_library() -> list[str]:
    return ["Dune", "The Name of the Wind", "Mistborn"]


# Will use tool mode, because strict mode is incompatible with tool usage
@llm.format(mode="strict-or-tool")
class Book(BaseModel):
    title: str
    author: str


@llm.call("openai:gpt-4o-mini", format=Book, tools=[in_library])
def recommend_book(genre: str):
    return f"Recommend a {genre} book that is available in the library."


def main():
    response: llm.Response[Book] = recommend_book("fantasy")
    while tool_call := response.tool_call:
        output = recommend_book.toolkit.call(tool_call)
        response = recommend_book.resume(response, output)
    book: Book = response.format()
    print(f"Title: {book.title}")
    print(f"Author: {book.author}")


main()
