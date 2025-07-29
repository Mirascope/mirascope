import asyncio
import json
from dataclasses import dataclass

from mirascope import llm


@dataclass
class BookReservation:
    reservation_id: str
    title: str

    def json(self) -> str:
        return json.dumps({"reservation_id": self.reservation_id, "title": self.title})


@dataclass
class Library:
    books: list[str]


library = Library(books=["Mistborn", "Gödel, Escher, Bach", "Dune"])


@llm.context_tool()
def available_books(ctx: llm.Context[Library]) -> list[str]:
    """List all books available in the library."""
    return ["Mistborn", "Gödel, Escher, Bach", "Dune"]


@llm.context_tool()
async def reserve_book(ctx: llm.Context[Library], title: str) -> BookReservation:
    """Reserve a book for the user."""
    reservation_id = "abcd-1234..."
    await asyncio.sleep(0.1)  # Simulate writing to database
    return BookReservation(reservation_id=reservation_id, title=title)


@llm.context_call(model="openai:gpt-4o-mini", tools=[available_books, reserve_book])
def librarian(ctx: llm.Context[Library]):
    return "Help the user check book availability and make reservations."


async def main():
    ctx = llm.Context(deps=library)
    response: llm.Response = librarian(ctx)

    while tool_call := response.tool_call:
        print(f"Tool call: {tool_call.name}")
        tool = librarian.toolkit.get(tool_call)

        if reserve_book.defines(tool):
            output = await tool.call(ctx, tool_call)
            reservation: BookReservation = output.value
            print("📚 Book reserved! Confirmation details:")
            print(f"   Reservation ID: {reservation.reservation_id}")
            print(f"   Book: {reservation.title}")

            response = librarian.resume(ctx, response, output)
        elif (
            # This works even though we used available_books.to_async(), due to __eq__ override
            tool == available_books
        ):
            output = available_books.call(ctx, tool_call)
            books: list[str] = output.value
            print(f"Available books: {books}")
            response = librarian.resume(ctx, response, output)

    print(response)


if __name__ == "__main__":
    asyncio.run(main())
