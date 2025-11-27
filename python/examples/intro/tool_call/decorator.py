from mirascope import llm


@llm.tool()  # [!code highlight]
def available_library_books() -> list[str]:  # [!code highlight]
    return [
        "Mistborn by Brandon Sanderson",
        "The Name of the Wind by Patrick Rothfuss",
        "Too Like the Lightning by Ada Palmer",
        "Wild Seed by Octavia Butler",
    ]


@llm.call(
    "openai/gpt-5",
    tools=[available_library_books],
)
def librarian(query: str):
    return query


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
