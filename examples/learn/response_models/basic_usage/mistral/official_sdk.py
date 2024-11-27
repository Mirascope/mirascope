import os
from typing import cast

from mistralai import Mistral
from pydantic import BaseModel

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])


class Book(BaseModel):
    """An extracted book."""

    title: str
    author: str


def extract_book(text: str) -> Book:
    completion = client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": f"Extract {text}"}],
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
        tool_choice="any",
    )
    if (
        completion
        and (choices := completion.choices)
        and (tool_calls := choices[0].message.tool_calls)
    ):
        return Book.model_validate_json(cast(str, tool_calls[0].function.arguments))
    raise ValueError("No tool call found")


book = extract_book("The Name of the Wind by Patrick Rothfuss")
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'
