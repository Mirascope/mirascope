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


@llm.tool()
async def available_books() -> list[str]:
    """List all books available in the library."""
    await asyncio.sleep(0.1)  # Simulate fetching from database
    return ["Mistborn", "Gödel, Escher, Bach", "Dune"]


@llm.tool()
async def reserve_book(title: str) -> BookReservation:
    """Reserve a book for the user."""
    reservation_id = "abcd-1234..."
    await asyncio.sleep(0.1)  # Simulate writing to database
    return BookReservation(reservation_id=reservation_id, title=title)


@llm.call(model="openai:gpt-4o-mini", tools=[available_books, reserve_book])
def librarian():
    return "Help the user check book availability and make reservations."


async def main():
    response: llm.Response = await librarian()

    while tool_call := response.tool_call:
        print(f"Tool call: {tool_call.name}")
        tool = librarian.get_tool(tool_call)

        if tool == reserve_book:
            output = tool.call(tool_call)
            reservation: BookReservation = output.value
            print("📚 Book reserved! Confirmation details:")
            print(f"   Reservation ID: {reservation.reservation_id}")
            print(f"   Book: {reservation.title}")

            response = await librarian.resume(response, output)
        else:
            output = tool.call(tool_call)
            response = await librarian.resume(response, output)

    print(response)


if __name__ == "__main__":
    asyncio.run(main())
