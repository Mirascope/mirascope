"""
You can add examples to your tool definitions to help the model better use the tool.
Examples can be added for individual fields as well as for the entire model.
"""
import os

from pydantic import ConfigDict, Field

from mirascope.core.base import BaseTool
from mirascope.core.openai import openai_call

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


class FormatBook(BaseTool):
    """Returns the title and author of a book nicely formatted."""

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


@openai_call(model="gpt-4o", tools=[FormatBook], tool_choice="required")
def recommend_book():
    """Recommend a nonfiction book for me to read."""


response = recommend_book()
if tool := response.tool:
    print(tool.call())
    # > Sapiens: A Brief History of Humankind by Harari, Yuval Noah
