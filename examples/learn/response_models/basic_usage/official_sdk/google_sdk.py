from google.genai import Client
from google.genai.types import FunctionDeclaration, Tool
from proto.marshal.collections import RepeatedComposite
from pydantic import BaseModel

client = Client()


class Book(BaseModel):
    """An extracted book."""

    title: str
    author: str


def extract_book(text: str) -> Book:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents={"parts": [{"text": f"Extract {text}"}]},
        config={
            "tools": [
                Tool(
                    function_declarations=[
                        FunctionDeclaration(
                            **{
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
                            }
                        )
                    ]
                )
            ],
            "tool_config": {
                "function_calling_config": {
                    "mode": "any",
                    "allowed_function_names": ["Book"],
                }
            },  # pyright: ignore [reportArgumentType]
        },
    )
    if tool_calls := [
        function_call
        for function_call in (response.function_calls or [])
        if function_call.args
    ]:
        return Book.model_validate(
            {
                k: v if not isinstance(v, RepeatedComposite) else list(v)
                for k, v in (tool_calls[0].args or {}).items()
            }
        )
    raise ValueError("No tool call found")


book = extract_book("The Name of the Wind by Patrick Rothfuss")
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'
