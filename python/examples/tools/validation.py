from mirascope import llm


@llm.tool()
def available_books() -> list[str]:
    """List the available books in the library."""
    return ["Mistborn", "Gödel, Escher, Bach", "Dune"]


@llm.call(model="openai:gpt-4o-mini", tools=[available_books])
def librarian(genre: str):
    return f"Recommend an available book in {genre}"


def main():
    response: llm.Response = librarian("fantasy")
    while tool_call := response.tool_call:
        tool: llm.Tool | None
        try:
            tool = response.tool(tool_call)
        except llm.ToolNotFoundError:
            print("Tool not found!")
            exit(1)
        try:
            output = tool.call()
        except Exception:
            print("Error while validating or calling tool!")
            exit(1)
        response = librarian.resume(response, output)

    print(response.text)


if __name__ == "__main__":
    main()
