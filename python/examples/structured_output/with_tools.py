from pydantic import BaseModel

from mirascope import llm

BOOK_DB = {
    "978-0-7653-1178-8": "Title: Mistborn, Author: Brandon Sanderson, Pages: 544"
}


class BookSummary(BaseModel):
    title: str
    author: str
    pages: int


@llm.tool
def get_book_info(isbn: str) -> str:
    """Look up book information by ISBN."""
    return BOOK_DB.get(isbn, "Book not found")


@llm.call("openai/gpt-5-mini", tools=[get_book_info], format=BookSummary)
def analyze_book(isbn: str):
    return f"Look up the book with ISBN {isbn} and summarize it."


response = analyze_book("978-0-7653-1178-8")

while response.tool_calls:
    tool_outputs = response.execute_tools()
    response = response.resume(tool_outputs)

summary: BookSummary = response.parse()
print(f"{summary.title} by {summary.author} ({summary.pages} pages)")
