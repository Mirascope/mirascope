from pydantic import ConfigDict, Field

from mirascope.core import BaseTool


class FormatBook(BaseTool):
    """Format a book's title and author."""

    title: str = Field(..., examples=["The Name of the Wind"])
    author: str = Field(..., examples=["Rothfuss, Patrick"])

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"title": "The Name of the Wind", "author": "Rothfuss, Patrick"}
            ]
        }
    )

    def call(self) -> str:
        return f"{self.title} by {self.author}"
