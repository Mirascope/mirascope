import asyncio
from dataclasses import dataclass

from mirascope import llm


@dataclass
class Library:
    available_books: list[str]


library = Library(available_books=["Mistborn", "Gödel, Escher, Bach", "Dune"])


@llm.tool(deps_type=Library)
def available_books(ctx: llm.Context[Library]) -> list[str]:
    """List the available books in the library."""
    return ctx.deps.available_books


@llm.call(model="openai:gpt-4o-mini", deps_type=Library, tools=[available_books])
def librarian(ctx: llm.Context[Library], genre: str):
    return f"Recommend an available book in {genre}"


async def main():
    with llm.context(deps=library) as ctx:
        stream: llm.AsyncStream[Library] = librarian.stream_async(ctx, "fantasy")
        while True:
            tool_output: llm.ToolOutput | None = None
            async for group in stream.groups():
                if group.type == "text":
                    async for chunk in group:
                        print(chunk)
                if group.type == "tool_call":
                    tool_call = await group.collect()
                    tool = stream.tool(tool_call)
                    tool_output = tool.call()
            if tool_output:
                stream = librarian.resume_stream_async(
                    stream.to_response(), tool_output
                )
            else:
                break


if __name__ == "__main__":
    asyncio.run(main())
