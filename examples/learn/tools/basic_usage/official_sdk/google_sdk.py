from google.genai import Client
from google.genai.types import FunctionDeclaration, GenerateContentConfig, Tool

client = Client()


def get_book_author(title: str) -> str:
    if title == "The Name of the Wind":
        return "Patrick Rothfuss"
    elif title == "Mistborn: The Final Empire":
        return "Brandon Sanderson"
    else:
        return "Unknown"


def identify_author(book: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents={"parts": [{"text": f"Who wrote {book}?"}]},
        config=GenerateContentConfig(
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
            ]
        ),
    )
    if tool_calls := [
        function_call
        for function_call in (response.function_calls or [])
        if function_call.args
    ]:
        if tool_calls[0].name == "get_book_author":
            return get_book_author(**dict((tool_calls[0].args or {}).items()))  # pyright: ignore [reportArgumentType]
    return response.text or ""


author = identify_author("The Name of the Wind")
print(author)
