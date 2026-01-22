from mirascope import llm


@llm.tool()  # [!code highlight]
def available_library_books() -> list[str]:  # [!code highlight]
    return [
        "Mistborn by Brandon Sanderson",
        "The Name of the Wind by Patrick Rothfuss",
        "Too Like the Lightning by Ada Palmer",
        "Wild Seed by Octavia Butler",
    ]


def librarian(query: str) -> llm.Response:
    model = llm.use_model("openai/gpt-5")
    message = llm.messages.user(query)
    return model.call(
        messages=[message],
        tools=[available_library_books],  # [!code highlight]
    )


def main():
    response: llm.Response = librarian(
        "Please recommend a mind-bending book that's available in the library."
    )

    # [!code highlight:4]
    while response.tool_calls:
        tool_outputs = response.execute_tools()
        response = response.resume(tool_outputs)

    print(response.pretty())


main()
