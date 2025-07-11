from mirascope import llm


@llm.tool()
def available_books() -> list[str]:
    """List the available books in the library."""
    return ["Mistborn", "Gödel, Escher, Bach", "Dune"]


@llm.call(model="openai:gpt-4o-mini", tools=[available_books])
def librarian(genre: str):
    return f"Recommend an available book in {genre}"


def main():
    stream: llm.Stream = librarian.stream("fantasy")
    while True:
        tool_call: llm.ToolCall | None = None
        for group in stream.groups():
            if group.type == "text":
                for chunk in group:
                    print(chunk)
            if group.type == "tool_call":
                tool_call = group.collect()
        if not tool_call:
            break
        tool_output = librarian.call_tool(tool_call)
        stream = librarian.resume_stream(stream, tool_output)


if __name__ == "__main__":
    main()
