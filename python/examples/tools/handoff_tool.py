from mirascope import llm


@llm.tool()
def available_books() -> list[str]:
    """List the available books in the library."""
    return ["Mistborn", "Gödel, Escher, Bach", "Dune"]


@llm.tool()
def ask_user_preference(question: str) -> str:
    """Ask the user for their preference when you need more specific information.
    Use this when you need to gather additional details from the user to make a better recommendation.
    """
    # This tool doesn't directly return data - it signals a handoff to get user input
    raise RuntimeError("Handoff tool should not be invoked.")


@llm.call(model="openai:gpt-4o-mini", tools=[available_books, ask_user_preference])
def librarian():
    return "Ask the user about their preferences, and then recommend an available book."


def main():
    response: llm.Response = librarian()

    while tool_call := response.tool_call:
        print(f"Tool call: {tool_call.name}")
        tool = response.tool(tool_call)
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
