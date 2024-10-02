from mirascope.core import BaseTool, mistral, prompt_template
from pydantic import ConfigDict, Field


class GetBookAuthor(BaseTool):
    """Returns the author of the book with the given title."""

    title: str = Field(
        ...,
        description="The title of the book.",
        examples=["The Name of the Wind"],
    )

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"title": "The Name of the Wind"}]}
    )

    def call(self) -> str:
        if self.title == "The Name of the Wind":
            return "Patrick Rothfuss"
        elif self.title == "Mistborn: The Final Empire":
            return "Brandon Sanderson"
        else:
            return "Unknown"


@mistral.call("mistral-large-latest", tools=[GetBookAuthor])
@prompt_template("Who wrote {book}?")
def identify_author(book: str): ...


response = identify_author("The Name of the Wind")
if tool := response.tool:
    print(tool.call())
else:
    print(response.content)
