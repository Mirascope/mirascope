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
def available_books() -> list[str]:
    """List all books available in the library."""
    return ["Mistborn", "Gödel, Escher, Bach", "Dune"]


@llm.tool()
def reserve_book(title: str) -> BookReservation:
    """Reserve a book for the user."""
    reservation_id = "abcd-1234..."
    return BookReservation(reservation_id=reservation_id, title=title)


@llm.call(model="openai:gpt-4o-mini", tools=[available_books, reserve_book])
def librarian():
    return "Help the user check book availability and make reservations."


def main():
    stream: llm.Stream = librarian.stream()
    while True:
        tool_call: llm.ToolCall | None = None
        for group in stream.groups():
            if group.type == "text":
                for chunk in group:
                    print(chunk, end="")
            if group.type == "tool_call":
                tool_call = group.collect()
        if not tool_call:
            break

        print(f"\nTool call: {tool_call.name}")
        tool = librarian.get_tool(tool_call)

        if tool == reserve_book:
            output = tool.call(tool_call)
            reservation: BookReservation = output.value
            print("📚 Book reserved! Confirmation details:")
            print(f"   Reservation ID: {reservation.reservation_id}")
            print(f"   Book: {reservation.title}")

            stream = librarian.resume_stream(stream, output)
        else:
            output = tool.call(tool_call)
            stream = librarian.resume_stream(stream, output)


if __name__ == "__main__":
    main()
