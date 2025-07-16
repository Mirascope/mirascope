import asyncio
from dataclasses import dataclass

from mirascope import llm


@dataclass
class Library:
    books: list[str]


library = Library(books=["Mistborn", "Gödel, Escher, Bach", "Dune"])


@llm.tool(deps_type=Library)
async def available_books(ctx: llm.Context[Library]) -> list[str]:
    """List the available books in the library."""
    await asyncio.sleep(0.1)  # Simulate fetching from database
    return ctx.deps.books


@llm.call(model="openai:gpt-4o-mini", deps_type=Library, tools=[available_books])
async def librarian(ctx: llm.Context[Library], genre: str):
    return f"Recommend an available book in {genre}"


async def main():
    ctx = llm.Context(deps=library)
    stream: llm.AsyncStream[Library] = await librarian.stream(ctx, "fantasy")
    while True:
        tool_output: llm.ToolOutput | None = None
        async for group in stream.groups():
            if group.type == "text":
                async for chunk in group:
                    print(chunk)
            if group.type == "tool_call":
                tool_call = await group.collect()
                tool_output = await librarian.toolkit.call(ctx, tool_call)
        if tool_output:
            stream = await librarian.resume_stream(stream, tool_output)
        else:
            break


if __name__ == "__main__":
    asyncio.run(main())
