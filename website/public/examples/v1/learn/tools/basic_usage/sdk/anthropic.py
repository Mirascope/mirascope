from anthropic import Anthropic

client = Anthropic()


# [!code highlight:8]
def get_book_author(title: str) -> str:
    if title == "The Name of the Wind":
        return "Patrick Rothfuss"
    elif title == "Mistborn: The Final Empire":
        return "Brandon Sanderson"
    else:
        return "Unknown"


def identify_author(book: str) -> str:
    message = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        messages=[{"role": "user", "content": f"Who wrote {book}?"}],
        # [!code highlight:12]
        tools=[
            {
                "name": "get_book_author",
                "description": "Returns the author of the book with the given title.",
                "input_schema": {
                    "properties": {"title": {"type": "string"}},
                    "required": ["title"],
                    "type": "object",
                },
            }
        ],
    )
    content = ""
    # [!code highlight:5]
    for block in message.content:
        if block.type == "tool_use":
            if block.name == "get_book_author":
                return get_book_author(**block.input)  # pyright: ignore [reportCallIssue]
        elif block.type == "text":
            content += block.text
        # Handle other content types appropriately
    return content


author = identify_author("The Name of the Wind")
print(author)
