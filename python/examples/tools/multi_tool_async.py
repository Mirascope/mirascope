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
    response: llm.Response = await librarian()
    while tool_calls := response.tool_calls:
        output = await librarian.call_tools(tool_calls)
        response = await librarian.resume_async(response, output)

    print(response)
    # > I recommend Mistborn, by Brandon Sanderson...


if __name__ == "__main__":
    asyncio.run(main())
