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
    stream: llm.Stream = librarian.stream()
    while True:
        tool_calls: list[llm.ToolCall] = []
        outputs: list[llm.ToolOutput] = []
        for group in stream.groups():
            if group.type == "text":
                for chunk in group:
                    print(chunk)
            if group.type == "tool_call":
                tool_call = group.collect()
                tool_calls.append(tool_call)
        if tool_calls:
            tools = stream.tools(tool_calls)
            outputs = [tool.call() for tool in tools]
            stream = librarian.resume_stream(stream.to_response(), outputs)
        else:
            break


if __name__ == "__main__":
    main()
