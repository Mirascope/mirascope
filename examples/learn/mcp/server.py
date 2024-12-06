"""Example of MCP server for book recommendations."""

import asyncio
from pathlib import Path

from mcp.types import Resource

from pydantic import AnyUrl

from mirascope.core import prompt_template
from mirascope.mcp import MCPServer


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


async def read_books_database():
    """Read the books database file."""
    data = Path(__file__).parent / "books.txt"
    with data.open() as f:
        return f.read()


@prompt_template()
def recommend_book(genre: str) -> str:
    """Get book recommendations by genre.

    Args:
        genre: Genre of book to recommend (fantasy, mystery, sci-fi, etc.)
    """
    return f"Recommend a {genre} book"


# Create a server for book recommendations
app = MCPServer(
    name="book-recommendations",  # Server name
    version="1.0.0",  # Server version
    tools=[get_book],  # Pre-register tools
    resources=[  # Pre-register resources
        (
            Resource(
                uri=AnyUrl("file://books.txt"),
                name="Books Database",
                mimeType="text/plain",
            ),
            read_books_database,
        )
    ],
    prompts=[recommend_book],  # Pre-register prompts
)


async def main():
    """Run the book recommendation server."""
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
