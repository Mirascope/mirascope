# pyright: reportCallIssue=false

from xai import Xai
from pydantic import BaseModel

# Note: The example has a type issue with calling Xai as a constructor
# It's intentionally suppressed with the pyright comment above
client = Xai()


class Book(BaseModel):
    """An extracted book."""

    title: str
    author: str


def extract_book(text: str) -> Book:
    completion = client.chat.completions.create(
        model="grok-3",
        messages=[{"role": "user", "content": f"Extract {text}"}],
         # [!code highlight:23]
        tools=[
            {
                "function": {
                    "name": "Book",
                    "description": "An extracted book.",
                    "parameters": {
                        "properties": {
                            "title": {"type": "string"},
                            "author": {"type": "string"},
                        },
                        "required": ["title", "author"],
                        "type": "object",
                    },
                },
                "type": "function",
            }
        ],
        tool_choice="required",
    )
    if tool_calls := completion.choices[0].message.tool_calls:
        return Book.model_validate_json(tool_calls[0].function.arguments)
    raise ValueError("No tool call found")


book = extract_book("The Name of the Wind by Patrick Rothfuss")
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss' # [!code highlight]
