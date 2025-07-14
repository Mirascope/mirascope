import asyncio

from mirascope import llm


@llm.tool()
def available_books() -> list[str]:
    """List the available books in the library."""
    return ["Mistborn", "Gödel, Escher, Bach", "Dune"]


@llm.call(model="openai:gpt-4o-mini", tools=[available_books])
async def librarian(genre: str):
    return f"Recommend an available book in {genre}"


async def main():
    response: llm.Response = await librarian("fantasy")
    while tool_call := response.tool_call:
        # Tool is sync, but use await because the call class is async
        output = await librarian.call_tool(tool_call)
        response = await librarian.resume_async(response, output)

    print(response)
    # "I recommend Mistborn, by Brandon Sanderson..."


if __name__ == "__main__":
    asyncio.run(main())
