from dataclasses import dataclass

from mirascope import llm


@dataclass
class Library:
    available_books: list[str]


library = Library(available_books=["Mistborn", "Gödel, Escher, Bach", "Dune"])


@dataclass
class SecretLibrary:
    special_book: str


secret_library = SecretLibrary(special_book="The Hitchhiker's Guide to the Galaxy")


@dataclass
class MetaLibrary:
    library: Library
    secret_library: SecretLibrary


meta_library = MetaLibrary(library=library, secret_library=secret_library)


# NOTE / TODO: It would be nice if we could define the tools in terms of their logical dep,
# and have a composition pattern, rather than needing to redefine the tools in terms of
# the composed dep.
@llm.tool(deps_type=MetaLibrary)
def available_books(ctx: llm.Context[MetaLibrary]) -> list[str]:
    """List the available books in the library."""
    return ctx.deps.library.available_books


# NOTE / TODO: It would be nice if we could define the tools in terms of their logical dep,
# and have a composition pattern, rather than needing to redefine the tools in terms of
# the composed dep.
@llm.tool(deps_type=MetaLibrary)
def secret_book(ctx: llm.Context[MetaLibrary]) -> str:
    """The special book from the secret library"""
    return ctx.deps.secret_library.special_book


@llm.call(
    model="openai:gpt-4o-mini",
    deps_type=MetaLibrary,
    tools=[available_books, secret_book],
)
def librarian(ctx: llm.Context[MetaLibrary], genre: str):
    return f"Recommend an available book in {genre}"


def main():
    with llm.context(deps=meta_library) as ctx:
        response: llm.Response[MetaLibrary] = librarian(ctx, "fantasy")
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
