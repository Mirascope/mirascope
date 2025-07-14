import asyncio

from mirascope import llm


@llm.tool()
def available_books() -> list[str]:
    """List the available books in the library."""
    return ["Mistborn", "Gödel, Escher, Bach", "Dune"]


@llm.tool()
async def book_rating(title: str) -> float:
    """Return the book's rating in stars (0.0 - 5.0)."""
    await asyncio.sleep(0.1)  # Simulate fetching from external source
    return 4.2


@llm.call(model="openai:gpt-4o-mini", tools=[available_books.to_async(), book_rating])
def librarian(genre: str):
    return f"Recommend an available book in {genre}"


async def main():
    response: llm.Response = await librarian("fantasy")
    while tool_call := response.tool_call:
        print(f"Tool call: {tool_call.name}")
        # Tool call: available_books
        output = await librarian.call_tool(tool_call)
        print(f"Tool returned: {output.value}")
        # Tool returned: ["Mistborn", "Gödel, Escher, Bach", "Dune"]
        response = await librarian.resume_async(response, output)

    print(response)
    # "I recommend Mistborn, by Brandon Sanderson..."


if __name__ == "__main__":
    asyncio.run(main())
