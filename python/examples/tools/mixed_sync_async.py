import asyncio
import inspect

from mirascope import llm


@llm.tool
def available_books() -> list[str]:
    """List the available books in the library."""
    return ["Mistborn", "Gödel, Escher, Bach", "Dune"]


@llm.tool
async def book_rating(title: str) -> float:
    """Return the book's rating in stars (0.0 - 5.0)."""
    await asyncio.sleep(0.1)  # Simulate fetching from external source
    return 4.2


@llm.call(model="openai:gpt-4o-mini", tools=[available_books, book_rating])
def librarian(genre: str):
    return f"Recommend an available book in {genre}, along with its rating."


def main():
    response: llm.Response = librarian("fantasy")
    while tool_calls := response.tool_calls:
        tool_outputs = []
        for call in tool_calls:
            output = librarian.toolkit.call(call)
            if inspect.isawaitable(output):
                output = asyncio.wait_for(output, timeout=1000)
            tool_outputs.append(output)
        response = librarian.resume(response, tool_outputs)

    print(response)
    # > I recommend Mistborn, by Brandon Sanderson, with a rating of 4.2...


if __name__ == "__main__":
    main()
