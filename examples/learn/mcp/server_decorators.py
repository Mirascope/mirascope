"""Example of MCP server for book recommendations."""

import asyncio
from pathlib import Path

from mirascope.mcp import MCPServer

# Create a server for book recommendations
app = MCPServer("book-recommendations")


@app.tool()
def get_book(genre: str) -> str:
    """Get a recommendation for a specific book genre.

    Args:
        genre: Genre of book (fantasy, mystery, sci-fi, etc.)
    """
    book_recommendations = {
        "fantasy": "The Name of the Wind by Patrick Rothfuss",
        "mystery": "The Silent Patient by Alex Michaelides",
        "sci-fi": "Project Hail Mary by Andy Weir",
        "romance": "The Love Hypothesis by Ali Hazelwood",
        "historical": "The Seven Husbands of Evelyn Hugo by Taylor Jenkins Reid",
    }
    return book_recommendations.get(genre, "Please specify a valid genre")


@app.resource(
    uri="file://books.txt",
    name="Books Database",
    mime_type="text/plain",
    description="Curated database of book recommendations by genre",
)
async def read_books_database():
    """Read the books database file."""
    data = Path(__file__).parent / "books.txt"
    with data.open() as f:
        return f.read()


@app.prompt()
def recommend_book(genre: str) -> str:
    """Get book recommendations by genre.

    Args:
        genre: Genre of book to recommend (fantasy, mystery, sci-fi, etc.)
    """
    return f"Recommend a {genre} book"


async def main():
    """Run the book recommendation server."""
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
