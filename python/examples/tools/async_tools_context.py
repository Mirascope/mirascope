import asyncio
from dataclasses import dataclass

from mirascope import llm


@dataclass
class Library:
    books: list[str]


library = Library(books=["Mistborn", "Gödel, Escher, Bach", "Dune"])


@llm.context_tool()
async def available_books(ctx: llm.Context[Library]) -> list[str]:
    """List the available books in the library."""
    await asyncio.sleep(0.1)  # Simulate fetching from database
    return ctx.deps.books


@llm.context_call(model="openai:gpt-4o-mini", tools=[available_books])
async def librarian(ctx: llm.Context[Library], genre: str):
    return f"Recommend an available book in {genre}"


async def main():
    ctx = llm.Context(deps=library)
    response: llm.Response = await librarian.call(ctx, "fantasy")
    while tool_call := response.tool_call:
        print(f"Tool call: {tool_call.name}")
        # Tool call: available_books
        output = await librarian.toolkit.call(ctx, tool_call)
        print(f"Tool returned: {output.value}")
        # Tool returned: ["Mistborn", "Gödel, Escher, Bach", "Dune"]
        response = await librarian.resume(ctx, response, output)

    print(response)
    # > I recommend Mistborn, by Brandon Sanderson...


if __name__ == "__main__":
    asyncio.run(main())
