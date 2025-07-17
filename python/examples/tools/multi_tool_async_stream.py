import asyncio
from collections.abc import Awaitable

from mirascope import llm


@llm.tool
async def available_genres() -> list[str]:
    """List the available genres in the library."""
    return ["fantasy", "scifi", "philosophy"]


@llm.tool
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
async def librarian():
    return "Recommend one available book for each supported genre"


async def main():
    stream: llm.AsyncStream = await librarian.stream()
    while True:
        outputs: list[Awaitable[llm.ToolOutput]] = []
        async for group in stream.groups():
            if group.type == "text":
                async for chunk in group:
                    print(chunk)
            if group.type == "tool_call":
                tool_call = await group.collect()
                outputs.append(librarian.toolkit.call(tool_call))
        if not outputs:
            break

        results = await asyncio.gather(*outputs)
        stream = await librarian.resume_stream(stream, results)


if __name__ == "__main__":
    asyncio.run(main())
