"""
You can add examples to your tool definitions to help the model better use the tool.
Examples can be added for individual fields as well as for the entire model.
"""

from pydantic import ConfigDict, Field

from mirascope.openai import OpenAICall, OpenAICallParams, OpenAITool


class FormatBook(OpenAITool):
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


class BookRecommender(OpenAICall):
    prompt_template = "Recommend a nonfiction book for me to read."

    call_params = OpenAICallParams(tools=[FormatBook], tool_choice="required")


recommender = BookRecommender()
response = recommender.call()
if tool := response.tool:
    print(tool.call())
    # > Sapiens: A Brief History of Humankind by Harari, Yuval Noah
