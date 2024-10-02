from google.generativeai import GenerativeModel
from google.generativeai.types import FunctionDeclaration, Tool

model = GenerativeModel("gemini-1.5-flash")


def get_book_author(title: str) -> str:
    if title == "The Name of the Wind":
        return "Patrick Rothfuss"
    elif title == "Mistborn: The Final Empire":
        return "Brandon Sanderson"
    else:
        return "Unknown"


def identify_author(book: str) -> str:
    response = model.generate_content(
        f"Who wrote {book}?",
        tools=[
            Tool(
                function_declarations=[
                    FunctionDeclaration(
                        **{
                            "name": "get_book_author",
                            "description": "Returns the author of the book with the given title.",
                            "parameters": {
                                "properties": {"title": {"type": "string"}},
                                "required": ["title"],
                                "type": "object",
                            },
                        }
                    )
                ]
            )
        ],
    )
    if tool_calls := [
        part.function_call for part in response.parts if part.function_call.args
    ]:
        if tool_calls[0].name == "get_book_author":
            return get_book_author(**dict(tool_calls[0].args.items()))  # pyright: ignore [reportArgumentType]
    return response.text


author = identify_author("The Name of the Wind")
print(author)
