from dataclasses import dataclass

from mirascope import llm


@dataclass
class Library:
    available_books: list[str]


library = Library(available_books=["Mistborn", "Gödel, Escher, Bach", "Dune"])


@llm.tool(deps_type=Library)
def available_books(ctx: llm.Context[Library]) -> list[str]:
    """List the available books in the library."""
    return ctx.deps.available_books


@llm.call(model="openai:gpt-4o-mini", deps_type=Library, tools=[available_books])
def librarian(ctx: llm.Context[Library], genre: str):
    return f"Recommend an available book in {genre}"


def main():
    with llm.context(deps=library) as ctx:
        stream: llm.Stream[Library] = librarian.stream(ctx, "fantasy")
        while True:
            tool_call: llm.ToolCall | None = None
            for group in stream.groups():
                if group.type == "text":
                    for chunk in group:
                        print(chunk)
                if group.type == "tool_call":
                    tool_call = group.collect()
            if tool_call:
                tool = stream.tool(tool_call)
                tool_output = tool.call()
                stream = librarian.resume_stream(stream, tool_output)
            else:
                break


if __name__ == "__main__":
    main()
