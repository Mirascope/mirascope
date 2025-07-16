from mirascope import llm


@llm.tool()
def available_genres() -> list[str]:
    """List the available genres in the library."""
    return ["fantasy", "scifi", "philosophy"]


@llm.tool()
def books_in_genre(genre: str) -> list[str]:
    """List the available books in a given genre."""
    books = {
        "fantasy": ["Mistborn", "The Name of the Wind", "Lord of the Rings"],
        "scifi": ["Dune", "Foundation", "The Player of Games"],
        "philosophy": [
            "Gödel, Escher, Bach",
            "Man's Search for Meaning",
            "The Consolations of Philosophy",
        ],
    }
    return books.get(
        genre,
        [
            f"Error: Genre '{genre}' not found in library. Expected 'fantasy', 'scifi', or 'philosophy'"
        ],
    )


@llm.call(model="openai:gpt-4o-mini", tools=[available_genres, books_in_genre])
def librarian():
    return "Recommend one available book for each supported genre"


def main():
    response: llm.Response = librarian()
    while tool_calls := response.tool_calls:
        outputs = [librarian.toolkit.call(tool_call) for tool_call in tool_calls]
        response = librarian.resume(response, outputs)

    print(response)


if __name__ == "__main__":
    main()
