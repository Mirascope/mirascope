from anthropic import Anthropic
from pydantic import BaseModel

client = Anthropic()


class Book(BaseModel):
    title: str
    author: str


def extract_book() -> Book:
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "The Name of the Wind by Patrick Rothfuss"}
        ],
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


book = extract_book()
assert isinstance(book, Book)
print(book)
