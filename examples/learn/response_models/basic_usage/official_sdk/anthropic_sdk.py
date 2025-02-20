from anthropic import Anthropic
from pydantic import BaseModel

client = Anthropic()


class Book(BaseModel):
    """An extracted book."""

    title: str
    author: str


def extract_book(text: str) -> Book:
    message = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        messages=[{"role": "user", "content": f"Extract {text}"}],
        tools=[
            {
                "name": "Book",
                "description": "An extracted book.",
                "input_schema": {
                    "properties": {
                        "title": {"type": "string"},
                        "author": {"type": "string"},
                    },
                    "required": ["title", "author"],
                    "type": "object",
                },
            }
        ],
        tool_choice={"type": "tool", "name": "Book"},
    )
    for block in message.content:
        if block.type == "tool_use" and block.input is not None:
            return Book.model_validate(block.input)
    raise ValueError("No tool call found")


book = extract_book("The Name of the Wind by Patrick Rothfuss")
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'
