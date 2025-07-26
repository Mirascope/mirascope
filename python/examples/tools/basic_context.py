from dataclasses import dataclass

from mirascope import llm


@dataclass
class Library:
    books: list[str]


library = Library(books=["Mistborn", "Gödel, Escher, Bach", "Dune"])


@llm.context_tool()
def available_books(ctx: llm.Context[Library]) -> list[str]:
    """List the available books in the library."""
    return ctx.deps.books


@llm.context_call(model="openai:gpt-4o-mini", tools=[available_books])
def librarian(ctx: llm.Context[Library], genre: str):
    return f"Recommend an available book in {genre}"


def main():
    ctx = llm.Context(deps=library)
    response: llm.Response = librarian(ctx, "fantasy")
    while tool_call := response.tool_call:
        print(f"Tool call: {tool_call.name}")
        # Tool call: available_books
        output = librarian.toolkit.call(ctx, tool_call)
        print(f"Tool returned: {output.value}")
        # Tool returned: ["Mistborn", "Gödel, Escher, Bach", "Dune"]
        response = librarian.resume(ctx, response, output)

    print(response)
    # > I recommend Mistborn, by Brandon Sanderson...


if __name__ == "__main__":
    main()
