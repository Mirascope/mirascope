from mirascope import llm


@llm.tool()
def available_genres() -> list[str]:
    """List the available genres in the library."""
    return ["fantasy", "scifi", "philosophy"]


@llm.tool()
def books_in_genre(genre: str) -> list[str]:
    """List the available books in a given genre."""
    if genre == "fantasy":
        return ["Mistborn", "The Name of the Wind", "Lord of the Rings"]
    elif genre == "scifi":
        return ["Dune", "Foundation", "The Player of Games"]
    elif genre == "philosophy":
        return [
            "Gödel, Escher, Bach",
            "Man's Search for Meaning",
            "The Consolations of Philosophy",
        ]
    else:
        raise KeyError()


@llm.call(model="openai:gpt-4o-mini", tools=[available_genres, books_in_genre])
def librarian():
    return "Recommend one available book for each supported genre"


def main():
    response: llm.Response = librarian()
    while tool_calls := response.tool_calls:
        outputs: list[llm.ToolOutput] = []
        for call in tool_calls:
            tool = response.to_tool(call)
            outputs.append(tool.call())

        response = librarian.resume(response, outputs)

    print(response.text)


if __name__ == "__main__":
    main()
