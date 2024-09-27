from google.generativeai import GenerativeModel
from google.generativeai.types import FunctionDeclaration, Tool, content_types
from proto.marshal.collections import RepeatedComposite
from pydantic import BaseModel

model = GenerativeModel("gemini-1.5-flash")


class Book(BaseModel):
    """An extracted book."""

    title: str
    author: str


def extract_book(text: str) -> Book:
    response = model.generate_content(
        f"Extract {text}",
        tools=[
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
        tool_config=content_types.to_tool_config(
            {
                "function_calling_config": {
                    "mode": "any",
                    "allowed_function_names": ["Book"],
                }
            }  # pyright: ignore [reportArgumentType]
        ),
    )
    if tool_calls := [
        part.function_call for part in response.parts if part.function_call.args
    ]:
        return Book.model_validate(
            {
                k: v if not isinstance(v, RepeatedComposite) else list(v)
                for k, v in tool_calls[0].args.items()
            }
        )
    raise ValueError("No tool call found")


book = extract_book("The Name of the Wind by Patrick Rothfuss")
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'
