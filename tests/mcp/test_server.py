"""Tests for MCP server implementation."""

import asyncio
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.types import Resource, Tool
from pydantic import AnyUrl, BaseModel

from mirascope.core import BaseMessageParam, prompt_template
from mirascope.core.anthropic import AnthropicTool
from mirascope.core.base import BaseTool, ImagePart, TextPart
from mirascope.mcp import MCPTool
from mirascope.mcp.server import (
    MCPServer,
    _convert_base_message_param_to_prompt_messages,
    _generate_prompt_from_function,
)


# Add fixtures for common test data
@pytest.fixture
def sample_tool():
    def recommend_book(title: str, author: str):
        """Recommend a book with title and author.

        Args:
            title: Book title
            author: Book author
        """

    return recommend_book


def test_server_initialization():
    """Test server initialization with different configurations."""

    # Test with tools
    def recommend_fantasy_book():
        """Recommends a fantasy book."""

    class FantasyBook(BaseModel):
        """Fantasy book model."""

        title: str
        author: str

    class FantasyBookTool(AnthropicTool):
        """Fantasy book tool."""

        title: str
        author: str

        def call(self) -> str: ...

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

    async def read_data(): ...

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
    async def read_fantasy_books(): ...

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
    def fantasy_book_search(title: str) -> str:  # pyright: ignore [reportReturnType]
        """Search for fantasy books."""

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
    async def recommend_fantasy_book(subgenre: str):
        """Get fantasy book recommendations."""

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
    async def read_fantasy_books(): ...

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

        def call(self) -> str: ...

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
    def no_doc_func(x: str): ...

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
    def mytool(a: str) -> str: ...

    with pytest.raises(KeyError):
        # same tool name again to force a conflict
        @server.tool()
        def mytool(a: str) -> str: ...


def test_resource_decorator_name_conflict():
    server = MCPServer("test")

    @server.resource(uri="file://test.txt")
    def read_res(): ...

    with pytest.raises(KeyError):
        # same resource URI again
        @server.resource(uri="file://test.txt")
        def read_res2(): ...


def test_prompt_decorator_conflict():
    server = MCPServer("test")

    @server.prompt()
    def prompt_func(x: str): ...  # pyright: ignore [reportRedeclaration]

    with pytest.raises(KeyError):
        # same prompt name (prompt_func)
        @server.prompt()
        def prompt_func(y: int): ...


def test_resource_docstring():
    server = MCPServer("test")

    @server.resource(uri="file://docstring.txt")
    def read_with_doc():
        """Short description."""

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
    assert issubclass(tool_cls, BaseTool)
    # Check that tool was registered
    assert "MyToolModel" in server._tools


def test_tool_decorator_with_base_tool():
    class MyBaseTool(BaseTool):
        def call(self) -> str: ...

    server = MCPServer("test")
    tool_cls = server.tool()(MyBaseTool)
    assert issubclass(tool_cls, BaseTool)
    # Check registration
    assert "MyBaseTool" in server._tools


def test_tool_decorator_with_mcp_tool():
    class MyToolModel(BaseModel):
        name: str
        age: int

    MyMCPTool = MCPTool.type_from_base_model_type(MyToolModel)
    server = MCPServer("test")
    tool_cls = server.tool()(MyMCPTool)
    assert issubclass(tool_cls, MCPTool)
    # Check registration
    assert "MyToolModel" in server._tools


def test_prompt_decorator_with_template():
    server = MCPServer("test")

    @server.prompt("Recommend a {genre} book")
    def prompt_func(genre: str): ...

    assert "prompt_func" in server._prompts

    prompt_data, _ = server._prompts["prompt_func"]
    assert prompt_data.name == "prompt_func"
    assert isinstance(prompt_data.arguments, list)
    assert any(arg.name == "genre" for arg in prompt_data.arguments)


@pytest.mark.asyncio
async def test_list_resources_decorator():
    handler_list_resources = None

    def capture_list_resources():
        def decorator(func):
            nonlocal handler_list_resources
            handler_list_resources = func
            return func

        return decorator

    with patch("mirascope.mcp.server.Server") as MockServer:
        server_instance = MagicMock()
        server_instance.list_resources.side_effect = capture_list_resources
        server_instance.get_capabilities.return_value = {}
        server_instance.run = AsyncMock(return_value=None)

        MockServer.return_value = server_instance

        app = MCPServer("book-recommend")

        @app.tool()
        def get_book(genre: str) -> str: ...

        @app.resource(
            uri="file://fantasy-books.txt/",
            name="Fantasy Books",
            mime_type="text/plain",
        )
        async def read_data(): ...

        @app.prompt()
        def recommend_book(genre: str) -> str: ...

        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()

        with patch("mcp.server.stdio.stdio_server") as mock_stdio_server:
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value = (mock_read_stream, mock_write_stream)
            mock_stdio_server.return_value = mock_cm

            await app.run()

        # Check if list_resources handler was captured
        assert handler_list_resources is not None, "list_resources handler not captured"
        resources_list = await handler_list_resources()  # pyright: ignore [reportGeneralTypeIssues]
        assert isinstance(resources_list, list), (
            "Expected list from list_resources handler"
        )


@pytest.mark.asyncio
async def test_read_resource_decorator():
    handler_read_resource = None

    def capture_read_resource():
        def decorator(func):
            nonlocal handler_read_resource
            handler_read_resource = func
            return func

        return decorator

    with patch("mirascope.mcp.server.Server") as MockServer:
        server_instance = MagicMock()
        server_instance.read_resource.side_effect = capture_read_resource
        server_instance.get_capabilities.return_value = {}
        server_instance.run = AsyncMock(return_value=None)

        MockServer.return_value = server_instance

        app = MCPServer("book-recommend")

        @app.resource(
            uri="file://test-resource/", name="Test Resource", mime_type="text/plain"
        )
        def read_test():
            return "Test Resource Content"

        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()

        with patch("mcp.server.stdio.stdio_server") as mock_stdio_server:
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value = (mock_read_stream, mock_write_stream)
            mock_stdio_server.return_value = mock_cm

            await app.run()

        assert handler_read_resource is not None, "read_resource handler not captured"
        content = await handler_read_resource("file://test-resource/")  # pyright: ignore [reportGeneralTypeIssues]
        assert content == "Test Resource Content"


@pytest.mark.asyncio
async def test_list_tools_decorator():
    handler_list_tools = None

    def capture_list_tools():
        def decorator(func):
            nonlocal handler_list_tools
            handler_list_tools = func
            return func

        return decorator

    with patch("mirascope.mcp.server.Server") as MockServer:
        server_instance = MagicMock()
        server_instance.list_tools.side_effect = capture_list_tools
        server_instance.get_capabilities.return_value = {}
        server_instance.run = AsyncMock(return_value=None)

        MockServer.return_value = server_instance

        app = MCPServer("book-recommend")

        @app.tool()
        def sample_tool(x: str) -> str: ...

        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()

        with patch("mcp.server.stdio.stdio_server") as mock_stdio_server:
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value = (mock_read_stream, mock_write_stream)
            mock_stdio_server.return_value = mock_cm

            await app.run()

        assert handler_list_tools is not None, "list_tools handler not captured"
        tools_list = await handler_list_tools()  # pyright: ignore [reportGeneralTypeIssues]
        assert isinstance(tools_list, list), "Expected list from list_tools handler"


@pytest.mark.asyncio
async def test_call_tool_decorator():
    handler_call_tool = None

    def capture_call_tool():
        def decorator(func):
            nonlocal handler_call_tool
            handler_call_tool = func
            return func

        return decorator

    with patch("mirascope.mcp.server.Server") as MockServer:
        server_instance = MagicMock()
        server_instance.call_tool.side_effect = capture_call_tool
        server_instance.get_capabilities.return_value = {}
        server_instance.run = AsyncMock(return_value=None)

        MockServer.return_value = server_instance

        app = MCPServer("book-recommend")

        @app.tool()
        def sample_tool(x: str) -> str:
            return f"Result for {x}"

        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()

        with patch("mcp.server.stdio.stdio_server") as mock_stdio_server:
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value = (mock_read_stream, mock_write_stream)
            mock_stdio_server.return_value = mock_cm

            await app.run()

        assert handler_call_tool is not None, "call_tool handler not captured"
        tool_result = await handler_call_tool("sample_tool", {"x": "test"})  # pyright: ignore [reportGeneralTypeIssues]
        assert isinstance(tool_result, list), "Expected list from call_tool handler"


@pytest.mark.asyncio
async def test_list_prompts_decorator():
    handler_list_prompts = None

    def capture_list_prompts():
        def decorator(func):
            nonlocal handler_list_prompts
            handler_list_prompts = func
            return func

        return decorator

    with patch("mirascope.mcp.server.Server") as MockServer:
        server_instance = MagicMock()
        server_instance.list_prompts.side_effect = capture_list_prompts
        server_instance.get_capabilities.return_value = {}
        server_instance.run = AsyncMock(return_value=None)

        MockServer.return_value = server_instance

        app = MCPServer("book-recommend")

        @app.prompt()
        def sample_prompt(x: str) -> str: ...

        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()

        with patch("mcp.server.stdio.stdio_server") as mock_stdio_server:
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value = (mock_read_stream, mock_write_stream)
            mock_stdio_server.return_value = mock_cm

            await app.run()

        assert handler_list_prompts is not None, "list_prompts handler not captured"
        prompts_list = await handler_list_prompts()  # pyright: ignore [reportGeneralTypeIssues]
        assert isinstance(prompts_list, list), "Expected list from list_prompts handler"


@pytest.mark.asyncio
async def test_get_prompt_decorator():
    handler_get_prompt = None

    def capture_get_prompt():
        def decorator(func):
            nonlocal handler_get_prompt
            handler_get_prompt = func
            return func

        return decorator

    with patch("mirascope.mcp.server.Server") as MockServer:
        server_instance = MagicMock()
        server_instance.get_prompt.side_effect = capture_get_prompt
        server_instance.get_capabilities.return_value = {}
        server_instance.run = AsyncMock(return_value=None)

        MockServer.return_value = server_instance

        app = MCPServer("book-recommend")

        @app.prompt()
        def sample_prompt(genre: str) -> str:
            return f"Prompt for {genre}"

        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()

        with patch("mcp.server.stdio.stdio_server") as mock_stdio_server:
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value = (mock_read_stream, mock_write_stream)
            mock_stdio_server.return_value = mock_cm

            await app.run()

        assert handler_get_prompt is not None, "get_prompt handler not captured"
        # Call the handler_get_prompt with some arguments
        prompt_result = await handler_get_prompt("sample_prompt", {"genre": "fantasy"})  # pyright: ignore [reportGeneralTypeIssues]
        # prompt_result should be a GetPromptResult or similar
        prompt_dict = prompt_result.dict()
        assert "messages" in prompt_dict, "get_prompt result should have messages"


def test_convert_base_message_param_to_prompt_messages_valid_str_user():
    # role: user, content: str
    param = BaseMessageParam(role="user", content="Hello")
    msgs = _convert_base_message_param_to_prompt_messages(param)
    assert len(msgs) == 1
    assert msgs[0].role == "user"  # pyright: ignore [reportAttributeAccessIssue]
    assert msgs[0].content.text == "Hello"  # pyright: ignore [reportAttributeAccessIssue]


def test_convert_base_message_param_to_prompt_messages_valid_str_assistant():
    # role: assistant, content: str
    param = BaseMessageParam(role="assistant", content="Hi there")
    msgs = _convert_base_message_param_to_prompt_messages(param)
    assert len(msgs) == 1
    assert msgs[0].role == "assistant"  # pyright: ignore [reportAttributeAccessIssue]
    assert msgs[0].content.text == "Hi there"  # pyright: ignore [reportAttributeAccessIssue]


def test_convert_base_message_param_to_prompt_messages_valid_iterable_text():
    # role: user, content: iterable of TextPart(type="text")
    param = BaseMessageParam(
        role="user",
        content=[
            TextPart(type="text", text="Part1"),
            TextPart(type="text", text="Part2"),
        ],
    )
    msgs = _convert_base_message_param_to_prompt_messages(param)
    assert len(msgs) == 2
    assert msgs[0].content.text == "Part1"  # pyright: ignore [reportAttributeAccessIssue]
    assert msgs[1].content.text == "Part2"  # pyright: ignore [reportAttributeAccessIssue]


def test_convert_base_message_param_to_prompt_messages_valid_iterable_image():
    # role: assistant, content: iterable of ImagePart(type="image")
    param = BaseMessageParam(
        role="assistant",
        content=[
            ImagePart(
                type="image",
                detail="An image",
                image=b"fakeimage",
                media_type="image/png",
            ),
        ],
    )
    msgs = _convert_base_message_param_to_prompt_messages(param)
    assert len(msgs) == 1
    assert msgs[0].role == "assistant"
    assert msgs[0].content.type == "image"
    assert msgs[0].content.mimeType == "image/png"
    assert msgs[0].content.data == "fakeimage"


def test_convert_base_message_param_to_prompt_messages_invalid_role():
    # invalid role
    param = BaseMessageParam(role="invalid", content="Hello")
    with pytest.raises(ValueError, match="invalid role"):
        _convert_base_message_param_to_prompt_messages(param)


def test_convert_base_message_param_to_prompt_messages_iterable_unknown_part():
    class UnknownPart:
        pass

    param = BaseMessageParam(role="user", content=[TextPart(type="text", text="Valid")])
    param.content = [UnknownPart()]  # pyright: ignore [reportAttributeAccessIssue]

    with pytest.raises(
        ValueError, match="Unsupported content type: <class '.*UnknownPart'>"
    ):
        _convert_base_message_param_to_prompt_messages(param)


def test_convert_base_message_param_to_prompt_messages_non_str_non_iterable():
    # content neither str nor iterable
    param = BaseMessageParam(role="user", content="Valid String")
    param.content = 12345  # pyright: ignore [reportAttributeAccessIssue]

    with pytest.raises(ValueError, match="Unsupported content type: <class 'int'>"):
        _convert_base_message_param_to_prompt_messages(param)


@pytest.mark.asyncio
async def test_constructor_with_prompts():
    @prompt_template()
    def recommend_book_prompt(genre: str) -> str:
        """Return a string recommending a book for the given genre."""
        return f"Recommend a {genre} book"

    app = MCPServer("book-recommend", prompts=[recommend_book_prompt])

    assert "recommend_book_prompt" in app._prompts

    mock_read_stream = AsyncMock()
    mock_write_stream = AsyncMock()

    with patch("mcp.server.stdio.stdio_server") as mock_stdio:
        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = (mock_read_stream, mock_write_stream)
        mock_stdio.return_value = mock_cm

        await app.run()

    (prompt, prompt_func) = app._prompts["recommend_book_prompt"]
    assert prompt.name == "recommend_book_prompt"
    assert (
        prompt.description == "Return a string recommending a book for the given genre."
    )
    assert isinstance(prompt.arguments, list)
    assert len(prompt.arguments) == 1
    assert prompt.arguments[0].name == "genre"

    result = prompt_func("fantasy")
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], BaseMessageParam)
    assert result[0].content == "Recommend a fantasy book"


@pytest.mark.asyncio
async def test_read_resource_decorator_non_existent():
    """Test reading a non-existent resource and expecting a ValueError."""
    handler_read_resource = None

    def capture_read_resource():
        def decorator(func):
            nonlocal handler_read_resource
            handler_read_resource = func
            return func

        return decorator

    with patch("mirascope.mcp.server.Server") as MockServer:
        server_instance = MagicMock()
        server_instance.read_resource.side_effect = capture_read_resource
        server_instance.get_capabilities.return_value = {}
        server_instance.run = AsyncMock(return_value=None)

        MockServer.return_value = server_instance

        # Create an MCPServer with no resources
        app = MCPServer("test")

        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()

        with patch("mcp.server.stdio.stdio_server") as mock_stdio_server:
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value = (mock_read_stream, mock_write_stream)
            mock_stdio_server.return_value = mock_cm

            await app.run()

        assert handler_read_resource is not None, "read_resource handler not captured"

        # Since no resources were defined, reading any URI should raise ValueError.
        with pytest.raises(ValueError, match="Unknown resource"):
            await handler_read_resource("file://nonexistent-resource/")  # pyright: ignore


@pytest.mark.asyncio
async def test_read_resource_decorator_async_function():
    """Test reading a resource from an async function using the captured handler."""
    handler_read_resource = None

    def capture_read_resource():
        def decorator(func):
            nonlocal handler_read_resource
            handler_read_resource = func
            return func

        return decorator

    with patch("mirascope.mcp.server.Server") as MockServer:
        server_instance = MagicMock()
        server_instance.read_resource.side_effect = capture_read_resource
        server_instance.get_capabilities.return_value = {}
        server_instance.run = AsyncMock(return_value=None)

        MockServer.return_value = server_instance

        app = MCPServer("test")

        @app.resource(uri="file://async-resource/")
        async def async_resource():
            # Simulate async work
            await asyncio.sleep(0.01)
            return "Async Resource Data"

        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()

        with patch("mcp.server.stdio.stdio_server") as mock_stdio_server:
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value = (mock_read_stream, mock_write_stream)
            mock_stdio_server.return_value = mock_cm

            await app.run()

        assert handler_read_resource is not None, "read_resource handler not captured"

        # Call the captured handler to read the async resource
        content = await handler_read_resource("file://async-resource/")  # pyright: ignore
        assert content == "Async Resource Data"


@pytest.mark.asyncio
async def test_call_tool_non_existent_tool():
    """Test calling a non-existent tool should raise KeyError."""
    handler_call_tool = None

    def capture_call_tool():
        def decorator(func):
            nonlocal handler_call_tool
            handler_call_tool = func
            return func

        return decorator

    with patch("mirascope.mcp.server.Server") as MockServer:
        server_instance = MagicMock()
        server_instance.call_tool.side_effect = capture_call_tool
        server_instance.get_capabilities.return_value = {}
        server_instance.run = AsyncMock(return_value=None)

        MockServer.return_value = server_instance

        # Create MCPServer with no tools
        app = MCPServer("test-call-tool")

        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()

        with patch("mcp.server.stdio.stdio_server") as mock_stdio_server:
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value = (mock_read_stream, mock_write_stream)
            mock_stdio_server.return_value = mock_cm

            await app.run()

        assert handler_call_tool is not None, "call_tool handler not captured"

        with pytest.raises(KeyError, match="Tool nonexistent_tool not found."):
            await handler_call_tool("nonexistent_tool", {})  # pyright: ignore


@pytest.mark.asyncio
async def test_call_tool_async_function():
    """Test calling a tool implemented as an async function."""
    handler_call_tool = None

    def capture_call_tool():
        def decorator(func):
            nonlocal handler_call_tool
            handler_call_tool = func
            return func

        return decorator

    with patch("mirascope.mcp.server.Server") as MockServer:
        server_instance = MagicMock()
        server_instance.call_tool.side_effect = capture_call_tool
        server_instance.get_capabilities.return_value = {}
        server_instance.run = AsyncMock(return_value=None)

        MockServer.return_value = server_instance

        app = MCPServer("test-async-tool")

        @app.tool()
        async def async_tool(x: str) -> str:
            await asyncio.sleep(0.01)
            return f"Async result for {x}"

        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()

        with patch("mcp.server.stdio.stdio_server") as mock_stdio_server:
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value = (mock_read_stream, mock_write_stream)
            mock_stdio_server.return_value = mock_cm

            await app.run()

        assert handler_call_tool is not None, "call_tool handler not captured"

        result = await handler_call_tool("async_tool", {"x": "test"})  # pyright: ignore
        # Should return a list of TextContent
        assert len(result) == 1
        assert result[0].text == "Async result for test"


@pytest.mark.asyncio
async def test_get_prompt_non_existent_prompt():
    """Test requesting a non-existent prompt should raise ValueError."""
    handler_get_prompt = None

    def capture_get_prompt():
        def decorator(func):
            nonlocal handler_get_prompt
            handler_get_prompt = func
            return func

        return decorator

    with patch("mirascope.mcp.server.Server") as MockServer:
        server_instance = MagicMock()
        server_instance.get_prompt.side_effect = capture_get_prompt
        server_instance.get_capabilities.return_value = {}
        server_instance.run = AsyncMock(return_value=None)

        MockServer.return_value = server_instance

        # Create MCPServer with no prompts
        app = MCPServer("test-get-prompt")

        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()

        with patch("mcp.server.stdio.stdio_server") as mock_stdio_server:
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value = (mock_read_stream, mock_write_stream)
            mock_stdio_server.return_value = mock_cm

            await app.run()

        assert handler_get_prompt is not None, "get_prompt handler not captured"

        with pytest.raises(ValueError, match="Unknown prompt: nonexistent_prompt"):
            await handler_get_prompt("nonexistent_prompt", {})  # pyright: ignore


@pytest.mark.asyncio
async def test_get_prompt_async_function():
    """Test requesting a prompt implemented as an async function."""
    handler_get_prompt = None

    def capture_get_prompt():
        def decorator(func):
            nonlocal handler_get_prompt
            handler_get_prompt = func
            return func

        return decorator

    with patch("mirascope.mcp.server.Server") as MockServer:
        server_instance = MagicMock()
        server_instance.get_prompt.side_effect = capture_get_prompt
        server_instance.get_capabilities.return_value = {}
        server_instance.run = AsyncMock(return_value=None)

        MockServer.return_value = server_instance

        app = MCPServer("test-async-prompt")

        @app.prompt()
        async def async_prompt(genre: str) -> list[BaseMessageParam]:
            await asyncio.sleep(0.01)
            return [BaseMessageParam(role="user", content=f"Async prompt for {genre}")]

        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()

        with patch("mcp.server.stdio.stdio_server") as mock_stdio_server:
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value = (mock_read_stream, mock_write_stream)
            mock_stdio_server.return_value = mock_cm

            await app.run()

        assert handler_get_prompt is not None, "get_prompt handler not captured"

        prompt_result = await handler_get_prompt("async_prompt", {"genre": "fantasy"})  # pyright: ignore
        # Should return a GetPromptResult with messages
        prompt_dict = prompt_result.dict()
        assert "messages" in prompt_dict
        assert len(prompt_dict["messages"]) == 1
        assert (
            prompt_dict["messages"][0]["content"]["text"] == "Async prompt for fantasy"
        )


@pytest.mark.asyncio
async def test_get_prompt_no_arguments():
    """Test get_prompt handler when arguments is None."""
    handler_get_prompt = None

    def capture_get_prompt():
        def decorator(func):
            nonlocal handler_get_prompt
            handler_get_prompt = func
            return func

        return decorator

    with patch("mirascope.mcp.server.Server") as MockServer:
        server_instance = MagicMock()
        server_instance.get_prompt.side_effect = capture_get_prompt
        server_instance.get_capabilities.return_value = {}
        server_instance.run = AsyncMock(return_value=None)

        MockServer.return_value = server_instance

        app = MCPServer("test-get-prompt-none-arguments")

        @app.prompt()
        def sample_prompt() -> str:
            """A prompt that recommends a book based on genre."""
            return "Recommend a fantasy book"

        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()

        with patch("mcp.server.stdio.stdio_server") as mock_stdio_server:
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value = (mock_read_stream, mock_write_stream)
            mock_stdio_server.return_value = mock_cm

            await app.run()

        assert handler_get_prompt is not None, "get_prompt handler not captured"
        prompt_result = await handler_get_prompt("sample_prompt", None)  # pyright: ignore

        prompt_dict = prompt_result.dict()
        assert "messages" in prompt_dict, "get_prompt result should have messages"
        assert len(prompt_dict["messages"]) == 1
        assert (
            prompt_dict["messages"][0]["content"]["text"] == "Recommend a fantasy book"
        )
