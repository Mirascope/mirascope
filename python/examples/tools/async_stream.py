import asyncio

from mirascope import llm


@llm.tool()
def available_books() -> list[str]:
    """List the available books in the library."""
    return ["Mistborn", "Gödel, Escher, Bach", "Dune"]


@llm.call(model="openai:gpt-4o-mini", tools=[available_books])
def librarian(genre: str):
    return f"Recommend an available book in {genre}"


async def main():
    stream: llm.AsyncStream = librarian.stream_async("fantasy")
    while True:
        tool_call: llm.ToolCall | None = None
        async for group in stream.groups():
            if group.type == "text":
                async for chunk in group:
                    print(chunk)
            if group.type == "tool_call":
                tool_call = await group.collect()
        if tool_call:
            tool_output = librarian.call_tool(tool_call)
            stream = librarian.resume_stream_async(stream.to_response(), tool_output)
        else:
            break


if __name__ == "__main__":
    asyncio.run(main())
