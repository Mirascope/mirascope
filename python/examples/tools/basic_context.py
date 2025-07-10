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
        response: llm.Response[Library] = librarian(ctx, "fantasy")
        while tool_call := response.tool_call:
            print(f"Tool call: {tool_call.name}")
            # Tool call: available_books
            tool = response.tool(tool_call)
            output = tool.call()
            print(f"Tool returned: {output.value}")
            # Tool returned: ["Mistborn", "Gödel, Escher, Bach", "Dune"]
            response = librarian.resume(response, output)

        print(response.text)
        "I recommend Mistborn, by Brandon Sanderson..."


if __name__ == "__main__":
    main()
