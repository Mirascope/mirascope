from dataclasses import dataclass

from mirascope import llm


@dataclass
class Library:
    books: list[str]


library = Library(books=["Mistborn", "Gödel, Escher, Bach", "Dune"])


@llm.tool(deps_type=Library)
def available_books(ctx: llm.Context[Library]) -> list[str]:
    """List the available books in the library."""
    return ctx.deps.books


@llm.tool()
def hardcoded_extra_book() -> str:
    """The special book that is always available, regardless of context"""
    return "The Hitchhiker's Guide to the Galaxy"


@llm.call(
    model="openai:gpt-4o-mini",
    deps_type=Library,
    tools=[available_books, hardcoded_extra_book],
)
def librarian(ctx: llm.Context[Library], genre: str):
    return f"Recommend an available book in {genre}"


def main():
    ctx = llm.Context(deps=library)
    response: llm.Response[Library] = librarian(ctx, "fantasy")
    while tool_calls := response.tool_calls:
        outputs = [librarian.toolkit.call(ctx, call) for call in tool_calls]
        response = librarian.resume(response, outputs)

    print(response)
    # > I recommend Mistborn, by Brandon Sanderson...


if __name__ == "__main__":
    main()
