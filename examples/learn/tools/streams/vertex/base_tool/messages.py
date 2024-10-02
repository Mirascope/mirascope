from mirascope.core import BaseTool, Messages, vertex
from pydantic import Field


class GetBookAuthor(BaseTool):
    """Returns the author of the book with the given title."""

    title: str = Field(..., description="The title of the book.")

    def call(self) -> str:
        if self.title == "The Name of the Wind":
            return "Patrick Rothfuss"
        elif self.title == "Mistborn: The Final Empire":
            return "Brandon Sanderson"
        else:
            return "Unknown"


@vertex.call("gemini-1.5-flash", tools=[GetBookAuthor], stream=True)
def identify_authors(books: list[str]) -> Messages.Type:
    return Messages.User(f"Who wrote {books}?")


stream = identify_authors(["The Name of the Wind", "Mistborn: The Final Empire"])
for chunk, tool in stream:
    if tool:  # will always be None, not supported at the provider level
        print(tool.call())
    else:
        print(chunk.content, end="", flush=True)
