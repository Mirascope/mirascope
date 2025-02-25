from mirascope import Messages, llm


def get_book_author(title: str) -> str:
    """Returns the author of the book with the given title

    Args:
        title: The title of the book.
    """
    if title == "The Name of the Wind":
        return "Patrick Rothfuss"
    elif title == "Mistborn: The Final Empire":
        return "Brandon Sanderson"
    else:
        return "Unknown"


@llm.call(provider="openai", model="gpt-4o-mini", tools=[get_book_author], stream=True)
def identify_authors(books: list[str]) -> Messages.Type:
    return Messages.User(f"Who wrote {books}?")


stream = identify_authors(["The Name of the Wind", "Mistborn: The Final Empire"])
for chunk, tool in stream:
    if tool:
        print(tool.call())
    else:
        print(chunk.content, end="", flush=True)
