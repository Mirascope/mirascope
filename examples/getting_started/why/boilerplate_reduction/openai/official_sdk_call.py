from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()


class Book(BaseModel):
    title: str
    author: str


def extract_book() -> Book:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "The Name of the Wind by Patrick Rothfuss"}
        ],
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


book = extract_book()
assert isinstance(book, Book)
print(book)
