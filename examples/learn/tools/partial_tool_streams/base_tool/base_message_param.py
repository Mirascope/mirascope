from mirascope import BaseMessageParam, BaseTool, llm
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


@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    tools=[GetBookAuthor],
    stream={"partial_tools": True},
)
def identify_authors(books: list[str]) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Who wrote {books}?")]


stream = identify_authors(["The Name of the Wind", "Mistborn: The Final Empire"])
for chunk, tool in stream:
    if tool:
        if tool.delta is not None:  # partial tool
            print(tool.delta)
        else:
            print(tool.call())
    else:
        print(chunk.content, end="", flush=True)
