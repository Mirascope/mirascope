import json

from litellm import completion


def get_book_author(title: str) -> str:
    if title == "The Name of the Wind":
        return "Patrick Rothfuss"
    elif title == "Mistborn: The Final Empire":
        return "Brandon Sanderson"
    else:
        return "Unknown"


def identify_author(book: str) -> str:
    response = completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Who wrote {book}"}],
        tools=[
            {
                "function": {
                    "name": "get_book_author",
                    "description": "Returns the author of the book with the given title.",
                    "parameters": {
                        "properties": {"title": {"type": "string"}},
                        "required": ["title"],
                        "type": "object",
                    },
                },
                "type": "function",
            }
        ],
    )
    if tool_calls := response.choices[0].message.tool_calls:  # pyright: ignore [reportAttributeAccessIssue]
        if tool_calls[0].function.name == "get_book_author":
            return get_book_author(**json.loads(tool_calls[0].function.arguments))
    return str(response.choices[0].message.content)  # pyright: ignore [reportAttributeAccessIssue]


author = identify_author("The Name of the Wind")
print(author)
