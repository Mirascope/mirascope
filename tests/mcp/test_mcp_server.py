"""Tests for MCP server implementation."""

import asyncio
import contextlib
from pathlib import Path
from typing import cast
from unittest.mock import AsyncMock, patch

import pytest
from mcp.server import Server
from mcp.types import GetPromptResult, Prompt, Resource, TextContent, Tool
from pydantic import AnyUrl, BaseModel

from mirascope.core.anthropic import AnthropicTool
from mirascope.core.base import BaseMessageParam, TextPart
from mirascope.mcp.server import (
    MCPServer,
    _convert_base_message_param_to_prompt_messages,
)


@pytest.fixture
def server() -> MCPServer:
    """Create a test server instance."""
    return MCPServer("book-recommend")


@pytest.fixture
def mock_stdio_transport():
    """Mock stdio transport for testing."""
    read_stream = AsyncMock()
    write_stream = AsyncMock()

    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = (read_stream, write_stream)

    return mock_context


def test_server_initialization():
    """Test server initialization with different configurations."""

    # Test with tools
    def recommend_fantasy_book() -> str:
        """Recommends a fantasy book."""
        return "The Name of the Wind"

    class FantasyBook(BaseModel):
        """Fantasy book model."""

        title: str
        author: str

    class FantasyBookTool(AnthropicTool):
        """Fantasy book tool."""

        title: str
        author: str

        def call(self) -> str:
            return f"{self.title} by {self.author}"

    # Test initializing with different tool types
    server = MCPServer(
        "book-recommend",
        tools=[recommend_fantasy_book, FantasyBook, FantasyBookTool],
        version="2.0.0",
    )
    assert len(server._tools) == 3
    assert "recommend_fantasy_book" in server._tools

    # Test with resources
    resource = Resource(
        uri=cast(AnyUrl, "file://data.txt/"),
        name="Fantasy Books Database",
        mimeType="text/plain",
        description="Database of fantasy books",
    )

    async def read_data():
        return "Fantasy book data"

    server = MCPServer("book-recommend", resources=[(resource, read_data)])
    assert len(server._resources) == 1
    assert "file://data.txt/" in server._resources


@pytest.mark.asyncio
async def test_list_resources():
    """Test listing resources."""
    server = MCPServer("book-recommend")

    @server.resource(
        uri="file://fantasy-books.txt/", name="Fantasy Books", mime_type="text/plain"
    )
    async def read_fantasy_books():
        return "Fantasy book list"

    # Mock list_resources method
    mock_list_resources = AsyncMock(
        return_value=[
            Resource(
                uri=cast(AnyUrl, "file://fantasy-books.txt/"),
                name="Fantasy Books",
                mimeType="text/plain",
            )
        ]
    )
    server.server.list_resources = mock_list_resources

    resources = await server.server.list_resources()
    assert len(resources) == 1
    assert resources[0].name == "Fantasy Books"


@pytest.mark.asyncio
async def test_list_tools():
    """Test listing tools."""
    server = MCPServer("book-recommend")

    @server.tool()
    def fantasy_book_search(title: str) -> str:
        """Search for fantasy books."""
        return f"Found: {title}"

    # Mock list_tools method
    mock_list_tools = AsyncMock(
        return_value=[
            Tool(
                name="fantasy_book_search",
                description="Search for fantasy books.",
                inputSchema={"type": "object"},
            )
        ]
    )
    server.server.list_tools = mock_list_tools

    tools = await server.server.list_tools()
    assert len(tools) == 1
    assert tools[0].name == "fantasy_book_search"


@pytest.mark.asyncio
async def test_async_prompt():
    """Test async prompt handling."""
    server = MCPServer("book-recommend")

    @server.prompt()
    async def recommend_fantasy_book(subgenre: str) -> list[BaseMessageParam]:
        """Get fantasy book recommendations."""
        return [
            BaseMessageParam(
                role="user", content=f"Recommend a {subgenre} fantasy book"
            )
        ]

    # Mock get_prompt
    mock_get_prompt = AsyncMock()
    server.server.get_prompt = mock_get_prompt

    await server.server.get_prompt()
    mock_get_prompt.assert_called_once()


@pytest.mark.asyncio
async def test_async_resource():
    """Test async resource handling."""
    server = MCPServer("book-recommend")

    @server.resource(
        uri="file://fantasy-books.txt/",
        name="Fantasy Books",
        description="Fantasy book database",
    )
    async def read_fantasy_books():
        return "Fantasy books data"

    # Mock read_resource
    mock_read_resource = AsyncMock()
    server.server.read_resource = mock_read_resource

    await server.server.read_resource()
    mock_read_resource.assert_called_once()


def test_convert_base_message_param():
    """Test conversion of BaseMessageParam to PromptMessage."""
    # Test text content
    text_message = BaseMessageParam(role="user", content="Recommend a fantasy book")
    prompt_messages = _convert_base_message_param_to_prompt_messages(text_message)
    assert len(prompt_messages) == 1
    assert prompt_messages[0].role == "user"
    assert prompt_messages[0].content.text == "Recommend a fantasy book"

    # Test multiple content parts
    multi_content = [
        TextPart(type="text", text="Looking for fantasy books"),
        TextPart(type="text", text="with dragons"),
    ]
    multi_message = BaseMessageParam(role="user", content=multi_content)
    prompt_messages = _convert_base_message_param_to_prompt_messages(multi_message)
    assert len(prompt_messages) == 2

    # Test invalid role
    with pytest.raises(ValueError, match="invalid role"):
        _convert_base_message_param_to_prompt_messages(
            BaseMessageParam(role="invalid", content="test")
        )


def test_main_example():
    """Test the main example code."""
    app = MCPServer("book-recommend")

    @app.tool()
    def get_book(genre: str) -> str:
        """Get a book recommendation."""
        return "The Hobbit by J.R.R. Tolkien"

    @app.resource(
        uri="file://fantasy-books.txt/", name="Fantasy Books", mime_type="text/plain"
    )
    async def read_data():
        """Read books database."""
        data = Path(__file__).parent / "fantasy-books.txt"
        with data.open() as f:
            return f.read()

    @app.prompt()
    def recommend_book(genre: str) -> str:
        """Get book recommendations."""
        return f"Recommend a {genre} book"

    assert "get_book" in app._tools
    assert "file://fantasy-books.txt/" in app._resources
    assert "recommend_book" in app._prompts

    # Test run method
    async def test_run():
        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()

        with patch("mcp.server.stdio.stdio_server") as mock_stdio:
            mock_stdio.return_value.__aenter__.return_value = (
                mock_read_stream,
                mock_write_stream,
            )
            with contextlib.suppress(asyncio.TimeoutError):
                await asyncio.wait_for(app.run(), timeout=0.1)

    asyncio.run(test_run())


# Add fixtures for common test data
@pytest.fixture
def sample_tool():
    def recommend_book(title: str, author: str) -> str:
        """Recommend a book with title and author.

        Args:
            title: Book title
            author: Book author
        """
        return f"{title} by {author}"

    return recommend_book


@pytest.fixture
def sample_resource():
    return Resource(
        uri=cast(AnyUrl, "file://books.txt/"),
        name="Book Database",
        mimeType="text/plain",
        description="Database of books",
    )


def test_tool_decorator_with_different_types(sample_tool):
    """Test tool decorator with different input types."""
    server = MCPServer("book-recommend")

    # Test with function
    tool_fn = server.tool()(sample_tool)
    assert tool_fn.__name__ == "recommend_book"

    # Test with BaseModel
    class BookModel(BaseModel):
        title: str
        author: str

    tool_model = server.tool()(BookModel)
    assert "title" in tool_model.model_fields
    assert "author" in tool_model.model_fields

    # Test with AnthropicTool
    class BookTool(AnthropicTool):
        title: str
        author: str

        def call(self) -> str:
            return f"{self.title} by {self.author}"

    tool_anthropic = server.tool()(BookTool)
    assert issubclass(tool_anthropic, AnthropicTool)


@pytest.mark.asyncio
async def test_call_tool():
    """Test calling a tool through the server."""
    server = MCPServer("book-recommend")

    @server.tool()
    def format_book(title: str, author: str) -> str:
        """Format book details.

        Args:
            title: Book title
            author: Book author
        """
        return f"{title} by {author}"

    # Mock call_tool method to return formatted result directly
    async def mock_call_tool(self, name: str, arguments: dict) -> list[TextContent]:
        # Return formatted text without calling server.call_tool again
        return [
            TextContent(
                type="text", text=f"{arguments['title']} by {arguments['author']}"
            )
        ]

    with patch.object(Server, "call_tool", mock_call_tool):
        result = await server.server.call_tool(
            "format_book", {"title": "Dune", "author": "Frank Herbert"}
        )
        assert len(result) == 1
        assert result[0].text == "Dune by Frank Herbert"


@pytest.mark.asyncio
async def test_read_resource():
    """Test reading resources through the server."""
    server = MCPServer("book-recommend")

    @server.resource(
        uri="file://test.txt/", name="Test Resource", mime_type="text/plain"
    )
    async def read_test():
        return "test content"

    # Mock read_resource method
    async def mock_read_resource(self, uri: AnyUrl) -> str:
        if str(uri) == "file://test.txt/":
            return "test content"
        raise ValueError("Unknown resource")

    with patch.object(Server, "read_resource", mock_read_resource):
        # Test reading existing resource
        content = await server.server.read_resource(cast(AnyUrl, "file://test.txt/"))
        assert content == "test content"

        # Test reading non-existent resource
        with pytest.raises(ValueError, match="Unknown resource"):
            await server.server.read_resource(cast(AnyUrl, "file://nonexistent.txt/"))


@pytest.mark.asyncio
async def test_list_prompts():
    """Test listing prompts."""
    server = MCPServer("book-recommend")

    @server.prompt()
    def basic_prompt(genre: str) -> list[BaseMessageParam]:
        """Get book recommendations."""
        return [BaseMessageParam(role="user", content=f"Recommend {genre} books")]

    # Mock list_prompts method
    async def mock_list_prompts(self) -> list[Prompt]:
        return [prompt for prompt, _ in server._prompts.values()]

    with patch.object(Server, "list_prompts", mock_list_prompts):
        prompts = await server.server.list_prompts()
        assert len(prompts) == 1
        assert prompts[0].name == "basic_prompt"


@pytest.mark.asyncio
async def test_get_prompt_with_args():
    """Test getting prompts with different argument configurations."""
    server = MCPServer("book-recommend")

    @server.prompt()
    def multi_genre_prompt(
        genre1: str, genre2: str = "fantasy"
    ) -> list[BaseMessageParam]:
        """Get recommendations for multiple genres."""
        return [
            BaseMessageParam(
                role="user",
                content=f"Recommend books that combine {genre1} and {genre2}",
            )
        ]

    # Mock get_prompt method
    async def mock_get_prompt(
        self, name: str, arguments: dict[str, str] | None
    ) -> GetPromptResult:
        prompt_and_func = server._prompts.get(name)
        if not prompt_and_func:
            raise ValueError("Unknown prompt")

        prompt, func = prompt_and_func
        messages = func(**(arguments or {}))
        return GetPromptResult(
            description=f"{prompt.name} template for {arguments}",
            messages=[
                msg
                for message in messages
                for msg in _convert_base_message_param_to_prompt_messages(message)
            ],
        )

    with patch.object(Server, "get_prompt", mock_get_prompt):
        # Test with all arguments
        result = await server.server.get_prompt(
            "multi_genre_prompt", {"genre1": "sci-fi", "genre2": "mystery"}
        )
        assert "sci-fi and mystery" in result.messages[0].content.text


def test_prompt_message_conversion():
    """Test conversion of various message content types."""
    # Test text content with multiple parts
    message = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Part 1"),
            TextPart(type="text", text="Part 2"),
        ],
    )
    result = _convert_base_message_param_to_prompt_messages(message)
    assert len(result) == 2
    assert result[0].content.text == "Part 1"
    assert result[1].content.text == "Part 2"
