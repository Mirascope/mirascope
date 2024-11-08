from typing import cast

from cohere import Client
from cohere.types import Tool, ToolParameterDefinitionsValue

client = Client()


def get_book_author(title: str) -> str:
    if title == "The Name of the Wind":
        return "Patrick Rothfuss"
    elif title == "Mistborn: The Final Empire":
        return "Brandon Sanderson"
    else:
        return "Unknown"


def identify_author(book: str) -> str:
    response = client.chat(
        model="command-r-plus",
        message=f"Who wrote {book}?",
        tools=[
            Tool(
                name="get_book_author",
                description="Returns the author of the book with the given title.",
                parameter_definitions={
                    "title": ToolParameterDefinitionsValue(
                        description=None, type="string", required=True
                    )
                },
            )
        ],
    )
    if tool_calls := response.tool_calls:
        if tool_calls[0].name == "get_book_author":
            return get_book_author(**(cast(dict[str, str], tool_calls[0].parameters)))
    return response.text


author = identify_author("The Name of the Wind")
print(author)
