from cohere import Client
from cohere.types import Tool, ToolParameterDefinitionsValue
from pydantic import BaseModel

client = Client()


class Book(BaseModel):
    """An extracted book."""

    title: str
    author: str


def extract_book(text: str) -> Book:
    response = client.chat(
        model="command-r-plus",
        message=f"Extract {text}",
        tools=[
            Tool(
                name="Book",
                description="An extracted book.",
                parameter_definitions={
                    "title": ToolParameterDefinitionsValue(
                        description=None, type="string", required=True
                    ),
                    "author": ToolParameterDefinitionsValue(
                        description=None, type="string", required=True
                    ),
                },
            )
        ],
    )
    if response.tool_calls:
        return Book.model_validate(response.tool_calls[0].parameters)
    raise ValueError("No tool call found")


book = extract_book("The Name of the Wind by Patrick Rothfuss")
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'
