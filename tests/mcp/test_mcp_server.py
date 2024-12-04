"""Tests for MCP server implementation."""

import asyncio
import contextlib
from pathlib import Path
from typing import cast
from unittest.mock import AsyncMock, patch

import pytest
from mcp.types import Resource, Tool
from pydantic import AnyUrl, BaseModel

from mirascope.core import BaseMessageParam
from mirascope.core.anthropic import AnthropicTool
from mirascope.core.base import BaseTool, ImagePart, TextPart
from mirascope.mcp.server import (
    MCPServer,
    _convert_base_message_param_to_prompt_messages,
    _generate_prompt_from_function,
)


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
    assert prompt_messages[0].role == "user"  # pyright: ignore [reportAttributeAccessIssue]
    assert prompt_messages[0].content.text == "Recommend a fantasy book"  # pyright: ignore [reportAttributeAccessIssue]

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
    assert result[0].content.text == "Part 1"  # pyright: ignore [reportAttributeAccessIssue]
    assert result[1].content.text == "Part 2"  # pyright: ignore [reportAttributeAccessIssue]


def test_convert_base_message_param_to_prompt_messages_invalid_role():
    # invalid role should raise ValueError
    with pytest.raises(ValueError, match="invalid role"):
        _convert_base_message_param_to_prompt_messages(
            BaseMessageParam(role="invalid", content="Test")
        )


def test_convert_base_message_param_to_prompt_messages_image_part():
    image_data = b"fakeimagebytes"
    # Provide all required fields for ImagePart
    part = ImagePart(
        type="image", detail="image detail", image=image_data, media_type="image/png"
    )
    message = BaseMessageParam(role="assistant", content=[part])
    result = _convert_base_message_param_to_prompt_messages(message)
    assert len(result) == 1
    assert result[0].role == "assistant"
    assert result[0].content.type == "image"
    assert result[0].content.mimeType == "image/png"
    assert result[0].content.data == image_data.decode("utf-8")


def test_generate_prompt_from_function_no_docstring():
    # function with no docstring
    def no_doc_func(x: str):
        return x

    prompt = _generate_prompt_from_function(no_doc_func)
    assert prompt.name == "no_doc_func"
    # no description
    assert prompt.description == ""
    assert isinstance(prompt.arguments, list)
    assert len(prompt.arguments) == 1
    assert prompt.arguments[0].name == "x"
    assert prompt.arguments[0].description == ""


def test_generate_prompt_from_function_with_docstring():
    # function with docstring and param desc
    def func_with_docs(x: str, y: int):
        """This is a test function.

        Args:
            x: The X parameter.
            y: The Y parameter.
        """
        return str(x) + str(y)

    prompt = _generate_prompt_from_function(func_with_docs)
    assert prompt.name == "func_with_docs"
    assert prompt.description == "This is a test function."
    assert isinstance(prompt.arguments, list)
    assert len(prompt.arguments) == 2
    arg_map = {arg.name: arg for arg in prompt.arguments}
    assert arg_map["x"].description == "The X parameter."
    assert arg_map["y"].description == "The Y parameter."


def test_tool_decorator_name_conflict():
    server = MCPServer("test")

    @server.tool()
    def mytool(a: str) -> str:
        return a

    with pytest.raises(KeyError):
        # same tool name again to force a conflict
        @server.tool()
        def mytool(a: str) -> str:
            return a


def test_resource_decorator_name_conflict():
    server = MCPServer("test")

    @server.resource(uri="file://test.txt")
    def read_res():
        return "data"

    with pytest.raises(KeyError):
        # same resource URI again
        @server.resource(uri="file://test.txt")
        def read_res2():
            return "data2"


def test_prompt_decorator_conflict():
    server = MCPServer("test")

    @server.prompt()
    def prompt_func(x: str):  # pyright: ignore [reportRedeclaration]
        return [BaseMessageParam(role="user", content="test")]

    with pytest.raises(KeyError):
        # same prompt name (prompt_func)
        @server.prompt()
        def prompt_func(y: int):
            return [BaseMessageParam(role="user", content="test2")]


def test_resource_docstring():
    server = MCPServer("test")

    @server.resource(uri="file://docstring.txt")
    def read_with_doc():
        """Short description."""
        return "hello"

    # The server normalizes the URI by adding a slash
    assert "file://docstring.txt/" in server._resources
    resource, _ = server._resources["file://docstring.txt/"]
    assert resource.description == "Short description."


def test_tool_decorator_with_base_model():
    class MyToolModel(BaseModel):
        name: str
        age: int

    server = MCPServer("test")

    tool_cls = server.tool()(MyToolModel)
    assert issubclass(tool_cls, AnthropicTool)
    # Check that tool was registered
    assert "MyToolModel" in server._tools


def test_tool_decorator_with_base_tool():
    class MyBaseTool(BaseTool):
        def call(self) -> str:
            return "called"

    server = MCPServer("test")
    tool_cls = server.tool()(MyBaseTool)
    assert issubclass(tool_cls, AnthropicTool)
    # Check registration
    assert "MyBaseTool" in server._tools


def test_prompt_decorator_with_template():
    server = MCPServer("test")

    @server.prompt("Recommend a {genre} book")
    def prompt_func(genre: str): ...

    assert "prompt_func" in server._prompts

    prompt_data, _ = server._prompts["prompt_func"]
    assert prompt_data.name == "prompt_func"
    assert isinstance(prompt_data.arguments, list)
    assert any(arg.name == "genre" for arg in prompt_data.arguments)
