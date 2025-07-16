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
    stream: llm.Stream = librarian.stream()
    while True:
        outputs: list[llm.ToolOutput] = []
        for group in stream.groups():
            if group.type == "text":
                for chunk in group:
                    print(chunk)
            if group.type == "tool_call":
                tool_call = group.collect()
                outputs.append(librarian.toolkit.call(tool_call))
        if not outputs:
            break
        stream = librarian.resume_stream(stream, outputs)


if __name__ == "__main__":
    main()
