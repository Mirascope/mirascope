from dataclasses import dataclass

from mirascope import llm


@dataclass
class Library:
    available_books: list[str]


@llm.tool(deps_type=Library)
def available_books(ctx: llm.Context[Library]) -> list[str]:
    """List the available books in the library."""
    return ctx.deps.available_books


@llm.tool(deps_type=Library)
def ask_user_preference(ctx: llm.Context[Library], question: str) -> str:
    """Ask the user for their preference when you need more specific information.
    Use this when you need to gather additional details from the user to make a better recommendation.
    """
    # This tool doesn't directly return data - it signals a handoff to get user input
    raise RuntimeError("Handoff tool should not be invoked.")


@llm.call(
    model="openai:gpt-4o-mini",
    deps_type=Library,
    tools=[available_books, ask_user_preference],
)
def librarian(ctx: llm.Context[Library]):
    return "Ask the user about their preferences, and then recommend an available book."


def main():
    library = Library(available_books=["Mistborn", "Gödel, Escher, Bach", "Dune"])
    with llm.context(deps=library) as ctx:
        response: llm.Response[Library] = librarian(ctx)

        while tool_call := response.tool_call:
            print(f"Tool call: {tool_call.name}")
            tool = response.to_tool(tool_call)
            if ask_user_preference.defines(tool):
                # TODO: Could we get better type hints for the args?
                question = tool_call.args.get("question")
                print(f"Librarian asks: {question}")
                user_input = input("Your response: ")
                output = llm.ToolOutput(id=tool_call.id, value=user_input)
                response = librarian.resume(response, output)

            else:
                output = tool.call()
                response = librarian.resume(response, output)

        print(response.text)


if __name__ == "__main__":
    main()
