import asyncio

from mirascope import llm


@llm.tool()
async def available_books() -> list[str]:
    """List the available books in the library."""
    await asyncio.sleep(0.1)  # Simulate fetching from database
    return ["Mistborn", "Gödel, Escher, Bach", "Dune"]


@llm.call(model="openai:gpt-4o-mini", tools=[available_books])
def librarian(genre: str):
    return f"Recommend an available book in {genre}"


async def main():
    stream: llm.AsyncStream = librarian.stream("fantasy")
    while True:
        tool_call: llm.ToolCall | None = None
        async for group in stream.groups():
            if group.type == "text":
                async for chunk in group:
                    print(chunk)
            if group.type == "tool_call":
                tool_call = await group.collect()
        if not tool_call:
            break
        tool_output = await librarian.call_tool(tool_call)
        stream = librarian.resume_stream(stream, tool_output)


if __name__ == "__main__":
    asyncio.run(main())
