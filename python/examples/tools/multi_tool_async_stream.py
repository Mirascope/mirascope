import asyncio

from mirascope import llm


@llm.tool()
async def available_genres() -> list[str]:
    """List the available genres in the library."""
    return ["fantasy", "scifi", "philosophy"]


@llm.tool()
async def books_in_genre(genre: str) -> list[str]:
    """List the available books in a given genre."""
    books = {
        "fantasy": ["Mistborn", "The Name of the Wind", "Lord of the Rings"],
        "scifi": ["Dune", "Foundation", "The Player of Games"],
        "philosophy": [
            "Gödel, Escher, Bach",
            "Man's Search for Meaning",
            "The Consolations of Philosophy",
        ],
    }
    return books.get(
        genre,
        [
            f"Error: Genre '{genre}' not found in library. Expected 'fantasy', 'scifi', or 'philosophy'"
        ],
    )


@llm.call(model="openai:gpt-4o-mini", tools=[available_genres, books_in_genre])
def librarian():
    return "Recommend one available book for each supported genre"


async def main():
    stream: llm.AsyncStream = librarian.stream()
    while True:
        tool_calls: list[llm.ToolCall] = []
        outputs: list[llm.ToolOutput] = []
        async for group in stream.groups():
            if group.type == "text":
                async for chunk in group:
                    print(chunk)
            if group.type == "tool_call":
                tool_call = await group.collect()
                tool_calls.append(tool_call)
        if not tool_calls:
            break
        outputs = await librarian.call_tools(tool_calls)
        stream = librarian.resume_stream(stream, outputs)


if __name__ == "__main__":
    asyncio.run(main())
