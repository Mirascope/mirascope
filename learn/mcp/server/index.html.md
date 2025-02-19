# MCP Server

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Tools](../tools.md)
    </div>

MCP (Model Context Protocol) Server in Mirascope enables you to expose resources, tools, and prompts to LLM clients through a standardized protocol. This allows for secure and controlled interactions between host applications (like Claude Desktop) and local services.

## Basic Usage and Syntax

Let's build a simple book recommendation server using MCP:

```python  hl_lines="7 10 27-32 40"
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
```

This example demonstrates:

1. Creating an MCP server with the `MCPServer` class
2. Registering a tool to get book recommendations by genre
3. Exposing a books database as a resource
4. Creating a prompt template for book recommendations
5. Running the server asynchronously

## Server Components

### Tools

Tools in MCP Server expose callable functions to clients. Tools can be registered using the `@app.tool()` decorator, which follows the same patterns as described in the [Tools](../tools.md) documentation:

```python
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
```

The `@app.tool()` decorator supports all the same functionality as the standard Mirascope tool decorators, including:

- Function-based tools
- Class-based tools inheriting from `BaseTool`
- Tool configurations and validation
- Computed fields and dynamic configuration

See the [Tools documentation](../tools.md) for more details on defining and using tools.

### Resources

Resources provide access to data through URIs. They can be registered using the `@app.resource()` decorator with configuration options:

```python
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
```

Resources support both synchronous and asynchronous functions, making them flexible for different types of data access.

### Prompts

Prompts define reusable message templates. They can be registered using the `@app.prompt()` decorator, which provides the same functionality as the standard Mirascope `@prompt_template` decorator described in the [Prompts](../prompts.md) documentation:

```python
    @app.prompt()
    def recommend_book(genre: str) -> str:
        """Get book recommendations by genre.

        Args:
            genre: Genre of book to recommend (fantasy, mystery, sci-fi, etc.)
        """
        return f"Recommend a {genre} book"
```

The `@app.prompt()` decorator supports all the features of standard Mirascope prompts, including:

- String templates
- Multi-line prompts
- Chat history
- Object attribute access
- Format specifiers
- Computed fields and dynamic configuration

See the [Prompts documentation](../prompts.md) for more details on creating and using prompts.

## Alternative Definition Style

In addition to using decorators, you can also define your functions first and then register them when creating the MCP server. This style enables better function reusability and separation of concerns:

```python hl_lines="46-59"
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
```

This alternative style offers several advantages:

1. **Function Reusability**: Functions can be used both independently and as part of the MCP server
2. **Cleaner Separation**: Clear separation between function definitions and server configuration
3. **Easier Testing**: Functions can be tested in isolation before being registered with the server
4. **Code Organization**: Related functions can be grouped together in separate modules

The same applies for prompts defined with `@prompt_template` - see the [Prompts](../prompts.md) documentation for more details about prompt reusability.

Both the decorator style and this alternative style are fully supported - choose the one that better fits your application's needs.

## Next Steps

By leveraging MCP Server in Mirascope, you can create secure and standardized integrations between LLM clients and local services. This enables powerful capabilities while maintaining control over how LLMs interact with your systems.
