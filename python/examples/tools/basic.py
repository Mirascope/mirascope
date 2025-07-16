from mirascope import llm


@llm.tool()
def available_books() -> list[str]:
    """List the available books in the library."""
    return ["Mistborn", "Gödel, Escher, Bach", "Dune"]


@llm.call(model="openai:gpt-4o-mini", tools=[available_books])
def librarian(genre: str):
    return f"Recommend a {genre} book that's available to rent."


def main():
    response: llm.Response = librarian("fantasy")
    while tool_call := response.tool_call:
        print(f"Tool call: {tool_call.name}")
        # Tool call: available_books
        output = librarian.toolkit.call(tool_call)
        print(f"Tool returned: {output.value}")
        # Tool returned: ["Mistborn", "Gödel, Escher, Bach", "Dune"]
        response = librarian.resume(response, output)

    print(response)
    # > I recommend Mistborn, by Brandon Sanderson...


if __name__ == "__main__":
    main()
