import asyncio
from dataclasses import dataclass

from mirascope import llm


@dataclass
class Library:
    books: dict[str, str]  # title -> author


@llm.tool
async def get_author(ctx: llm.Context[Library], title: str) -> str:
    """Get the author of a book."""
    return ctx.deps.books.get(title, "Book not found")


@llm.call("openai/gpt-5-mini", tools=[get_author])
async def librarian(ctx: llm.Context[Library], query: str):
    return query


async def main():
    library = Library(books={"Dune": "Frank Herbert", "Neuromancer": "William Gibson"})
    ctx = llm.Context(deps=library)
    response = await librarian(ctx, "Who wrote Dune?")

    while response.tool_calls:
        tool_outputs = await response.execute_tools(ctx)
        response = await response.resume(ctx, tool_outputs)

    print(response.pretty())
    # Dune was written by Frank Herbert.


asyncio.run(main())
