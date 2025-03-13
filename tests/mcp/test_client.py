import base64
from abc import update_abstractmethods
from contextlib import asynccontextmanager
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from anyio import create_memory_object_stream
from mcp.client.session import ClientSession as MCPClientSession
from mcp.client.stdio import (
    StdioServerParameters,
    get_default_environment,
)
from mcp.types import (
    BlobResourceContents,
    CallToolResult,
    EmbeddedResource,
    ImageContent,
    JSONRPCMessage,
    Prompt,
    PromptMessage,
    Resource,
    TextContent,
    TextResourceContents,
    Tool,
)
from pydantic import AnyUrl, BaseModel

from mirascope.core import BaseTool
from mirascope.core.base import AudioPart, DocumentPart, ImagePart, TextPart
from mirascope.mcp._utils import (
    build_object_type,
    convert_prompt_message_to_base_message_params,
    create_tool_from_mcp_tool,
    json_schema_to_python_type,
    read_stream_exception_filer,
    snake_to_pascal,
)
from mirascope.mcp.client import MCPClient, sse_client, stdio_client


@pytest.mark.asyncio
async def test_stdio_client() -> None:
    """Test stdio_client context manager."""
    send_read, receive_read = create_memory_object_stream(10)
    send_write, _ = create_memory_object_stream(10)

    @asynccontextmanager
    async def mock_client(server_params):
        await send_read.send(
            JSONRPCMessage(jsonrpc="2.0", method="initialized", id="init")  # pyright: ignore [reportCallIssue]
        )
        await send_read.aclose()
        yield receive_read, send_write

    class MockClientSession:
        def __init__(
            self,
            read,
            write,
            read_timeout_seconds=None,
            sampling_callback=None,
            list_roots_callback=None,
        ):
            self.read = read
            self.write = write

        async def __aenter__(self):
            # Just consume messages until 'initialized' appears
            async for msg in self.read:  # pragma: no cover
                if msg.root.method == "initialized":
                    break
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

        async def initialize(self):
            return

    with (
        patch("mirascope.mcp.client.mcp_stdio_client", new=mock_client),
        patch("mirascope.mcp.client.ClientSession", new=MockClientSession),
    ):
        params = StdioServerParameters(command="fake_cmd", args=[], env=None)
        async with stdio_client(params) as client:
            assert isinstance(client, MCPClient)

    send_read, receive_read = create_memory_object_stream(10)
    send_write, _ = create_memory_object_stream(10)

    with (
        patch("mirascope.mcp.client.mcp_sse_client", new=mock_client),
        patch("mirascope.mcp.client.ClientSession", new=MockClientSession),
    ):
        async with sse_client("http://example.com") as client:
            assert isinstance(client, MCPClient)


def test_get_default_environment():
    # Test get_default_environment from stdio.py
    env = get_default_environment()
    # We can't guarantee specific keys, but we ensure it's a dict
    assert isinstance(env, dict)


@pytest.mark.asyncio
async def test_read_stream_exception_filer():
    send, receive = create_memory_object_stream(10)
    expect_exception = ValueError("Invalid")
    mock = MagicMock()
    async with read_stream_exception_filer(receive, mock) as filtered, send:
        # send a normal message
        await send.send(JSONRPCMessage(jsonrpc="2.0", id="ok", method="ok"))  # pyright: ignore [reportCallIssue]

        # send an exception
        await send.send(expect_exception)
        # send another normal message
        await send.send(JSONRPCMessage(jsonrpc="2.0", id="another", method="another"))  # pyright: ignore [reportCallIssue]
        await send.aclose()

        messages = []
        async for msg in filtered:
            messages.append(msg)
        assert len(messages) == 2
        assert messages[0].root.id == "ok"
        assert messages[1].root.id == "another"
        mock.assert_called_once_with(expect_exception)


@pytest.mark.asyncio
async def test_read_stream_exception_filer_no_handler():
    send, receive = create_memory_object_stream(10)

    async with read_stream_exception_filer(receive) as filtered, send:
        # send a normal message
        await send.send(JSONRPCMessage(jsonrpc="2.0", id="ok", method="ok"))  # pyright: ignore [reportCallIssue]

        # send an exception
        await send.send(ValueError("Invalid"))
        # send another normal message
        await send.send(JSONRPCMessage(jsonrpc="2.0", id="another", method="another"))  # pyright: ignore [reportCallIssue]
        await send.aclose()

        messages = []
        async for msg in filtered:
            messages.append(msg)
        assert len(messages) == 2
        assert messages[0].root.id == "ok"
        assert messages[1].root.id == "another"


def test_snake_to_pascal():
    # Test snake_to_pascal coverage
    assert snake_to_pascal("hello_world") == "HelloWorld"


def test_json_schema_to_python_type_all_cases():
    # Already tested some cases, add a fallback test
    assert json_schema_to_python_type({"type": "integer"}) is int
    assert json_schema_to_python_type({"type": "unknown_type"}) is Any
    # object without properties
    assert isinstance(json_schema_to_python_type({"type": "object"}), type)


def test_build_object_type_full():
    # Test more complex schema
    properties = {
        "str_field": {"type": "string", "description": "str desc"},
        "num_field": {"type": "number"},
        "arr_field": {"type": "array", "items": {"type": "integer"}},
        "obj_field": {
            "type": "object",
            "properties": {"inner": {"type": "boolean"}},
            "required": ["inner"],
        },
    }
    required = ["str_field"]
    Model = build_object_type(properties, required, "ComplexModel")
    instance = Model(str_field="abc", obj_field={"inner": True})
    assert instance.str_field == "abc"  # pyright: ignore [reportAttributeAccessIssue]
    assert instance.obj_field.inner is True  # pyright: ignore [reportAttributeAccessIssue]
    assert instance.num_field is None  # pyright: ignore [reportAttributeAccessIssue]
    assert instance.arr_field is None  # pyright: ignore [reportAttributeAccessIssue]


def test_create_model_from_tool_extra():
    tool = Tool(
        name="extra_tool",
        inputSchema={
            "type": "object",
            "properties": {
                "opt_str": {"type": "string", "description": "optional string"},
                "req_arr": {"type": "array", "items": {"type": "integer"}},
            },
            "required": ["req_arr"],
        },
    )

    Model = create_tool_from_mcp_tool(tool)
    Model.call = lambda self: None  # pyright: ignore [reportAttributeAccessIssue]
    update_abstractmethods(Model)
    instance = Model(req_arr=[1, 2, 3])  # pyright: ignore [reportCallIssue]
    assert instance.req_arr == [1, 2, 3]  # pyright: ignore [reportAttributeAccessIssue]
    assert instance.opt_str is None  # pyright: ignore [reportAttributeAccessIssue]


def test_convert_prompt_message_all_content_types():
    # Test coverage for all content branches
    # TextContent
    pm_text = PromptMessage(role="user", content=TextContent(type="text", text="hi"))
    res_text = convert_prompt_message_to_base_message_params(pm_text)
    assert res_text.content == "hi"

    # ImageContent
    img_data = base64.b64encode(b"fake_img").decode()
    pm_img = PromptMessage(
        role="assistant",
        content=ImageContent(type="image", data=img_data, mimeType="image/png"),
    )
    res_img = convert_prompt_message_to_base_message_params(pm_img)
    assert isinstance(res_img.content[0], ImagePart)
    assert res_img.content[0].image == b"fake_img"

    # EmbeddedResource with TextResourceContents
    pm_embed_text = PromptMessage(
        role="assistant",
        content=EmbeddedResource(
            type="resource",
            resource=TextResourceContents(
                uri=AnyUrl("http://example.com"), text="embedded txt"
            ),
        ),
    )
    res_embed_text = convert_prompt_message_to_base_message_params(pm_embed_text)
    assert res_embed_text.content == "embedded txt"

    # EmbeddedResource with BlobResourceContents - image
    img_blob = base64.b64encode(b"someimg").decode()
    pm_embed_img = PromptMessage(
        role="assistant",
        content=EmbeddedResource(
            type="resource",
            resource=BlobResourceContents(
                uri=AnyUrl("http://example.com/img.png"),
                blob=img_blob,
                mimeType="image/png",
            ),
        ),
    )
    res_embed_img = convert_prompt_message_to_base_message_params(pm_embed_img)
    assert isinstance(res_embed_img.content[0], ImagePart)
    assert res_embed_img.content[0].image == b"someimg"

    # EmbeddedResource with BlobResourceContents - pdf
    pdf_blob = base64.b64encode(b"%PDF-fake").decode()
    pm_embed_pdf = PromptMessage(
        role="assistant",
        content=EmbeddedResource(
            type="resource",
            resource=BlobResourceContents(
                uri=AnyUrl("http://example.com/doc.pdf"),
                blob=pdf_blob,
                mimeType="application/pdf",
            ),
        ),
    )
    res_embed_pdf = convert_prompt_message_to_base_message_params(pm_embed_pdf)
    assert isinstance(res_embed_pdf.content[0], DocumentPart)
    assert res_embed_pdf.content[0].document == b"%PDF-fake"

    # EmbeddedResource with audio
    audio_blob = base64.b64encode(b"FAKEAUDIO").decode()
    pm_embed_audio = PromptMessage(
        role="assistant",
        content=EmbeddedResource(
            type="resource",
            resource=BlobResourceContents(
                uri=AnyUrl("http://example.com/sound.wav"),
                blob=audio_blob,
                mimeType="audio/wav",
            ),
        ),
    )
    res_embed_audio = convert_prompt_message_to_base_message_params(pm_embed_audio)
    assert isinstance(res_embed_audio.content[0], AudioPart)
    assert res_embed_audio.content[0].audio == b"FAKEAUDIO"

    # Unsupported mime
    unsupp_blob = base64.b64encode(b"FAKE").decode()
    pm_unsupp = PromptMessage.model_construct(
        role="assistant",
        content=EmbeddedResource(
            type="resource",
            resource=BlobResourceContents(
                uri=AnyUrl("http://example.com/file.xyz"),
                blob=unsupp_blob,
                mimeType="application/xyz",
            ),
        ),
        validate=False,
    )
    with pytest.raises(ValueError):
        convert_prompt_message_to_base_message_params(pm_unsupp)

    # Empty mime
    unsupp_blob = base64.b64encode(b"FAKE").decode()
    pm_unsupp = PromptMessage.model_construct(
        role="assistant",
        content=EmbeddedResource(
            type="resource",
            resource=BlobResourceContents(
                uri=AnyUrl("http://example.com/file.xyz"),
                blob=unsupp_blob,
                mimeType=None,
            ),
        ),
        validate=False,
    )
    with pytest.raises(ValueError):
        convert_prompt_message_to_base_message_params(pm_unsupp)

    # Invalid role
    pm_invalid_role = PromptMessage.model_construct(
        role="other", content=TextContent(type="text", text="hi"), validate=False
    )
    with pytest.raises(ValueError):
        convert_prompt_message_to_base_message_params(pm_invalid_role)

    # Unsupported content type
    class FakeContent(BaseModel):
        pass

    pm_unsupported_content = PromptMessage.model_construct(
        role="assistant", content=FakeContent(), validate=False
    )
    with pytest.raises(ValueError):
        convert_prompt_message_to_base_message_params(pm_unsupported_content)


@pytest.mark.asyncio
async def test_mcp_client_methods():
    # Test MCPClient methods: list_resources, read_resource, list_prompts, get_prompt_template, list_tools
    mock_session = AsyncMock(spec=MCPClientSession)
    mock_session.list_resources.return_value.resources = [
        Resource(uri=AnyUrl("http://example.com"), name="res1")
    ]
    mock_session.read_resource.return_value.contents = [
        TextResourceContents(uri=AnyUrl("http://example.com"), text="Hello"),
        BlobResourceContents(
            uri=AnyUrl("http://example.com"), blob=base64.b64encode(b"FAKE").decode()
        ),
    ]
    mock_session.list_prompts.return_value.prompts = [Prompt(name="p1")]
    mock_message = PromptMessage(
        role="assistant", content=TextContent(type="text", text="Hello from prompt")
    )
    mock_session.get_prompt.return_value = type(
        "MockPromptResult", (), {"messages": [mock_message]}
    )
    mock_tool = Tool(
        name="test_tool",
        inputSchema={
            "type": "object",
            "properties": {"genre": {"type": "string"}},
            "required": ["genre"],
        },
    )
    mock_session.list_tools.return_value.tools = [mock_tool]
    mock_session.call_tool.return_value = CallToolResult(
        isError=False, content=[TextContent(type="text", text="Tool result")]
    )

    client = MCPClient(mock_session)

    # list_resources
    res = await client.list_resources()
    assert len(res) == 1
    assert res[0].name == "res1"

    # read_resource
    contents = await client.read_resource("http://example.com")
    assert contents == [
        TextPart(type="text", text="Hello"),
        BlobResourceContents(
            uri=AnyUrl("http://example.com/"), mimeType=None, blob="RkFLRQ=="
        ),
    ]

    # list_prompts
    prompts = await client.list_prompts()
    assert prompts[0].name == "p1"

    # get_prompt_template and async_prompt execution
    async_prompt = await client.get_prompt_template("p1")
    prompt_result = await async_prompt(genre="mystery")
    assert prompt_result[0].content == "Hello from prompt"

    # list_tools
    tools = await client.list_tools()
    assert len(tools) == 1
    t = tools[0]
    assert issubclass(t, BaseTool)

    base_tool = BaseTool.type_from_base_model_type(t)
    ret = await base_tool(genre="fantasy").call()  # pyright: ignore [reportCallIssue, reportAbstractUsage]
    assert ret == ["Tool result"]


@pytest.mark.asyncio
async def test_mcp_client_tool_with_image():
    # Test a tool returning ImageContent or EmbeddedResource
    mock_session = AsyncMock(spec=MCPClientSession)
    img_data = base64.b64encode(b"IMAGEDATA").decode()
    mock_tools = [
        Tool(
            name="img_tool",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="img_tool",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="error_tool",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]
    mock_session.list_tools.return_value.tools = mock_tools
    mock_session.call_tool.return_value = CallToolResult(
        isError=False,
        content=[ImageContent(type="image", data=img_data, mimeType="image/png")],
    )

    client = MCPClient(mock_session)
    tools = await client.list_tools()
    tool = tools[0]
    base_tool = BaseTool.type_from_base_model_type(tool)
    result = await base_tool().call()  # pyright: ignore [reportAbstractUsage,reportCallIssue]
    assert len(result) == 1
    assert isinstance(result[0], ImageContent)

    # Test EmbeddedResource directly
    blob_data = base64.b64encode(b"SOMEDATA").decode()
    mock_session.call_tool.return_value = CallToolResult(
        isError=False,
        content=[
            EmbeddedResource(
                type="resource",
                resource=BlobResourceContents(
                    uri=AnyUrl("https://example.com"),
                    blob=blob_data,
                    mimeType="application/octet-stream",
                ),
            )
        ],
    )
    result = await base_tool().call()  # pyright: ignore [reportAbstractUsage]
    # In this case call returns the content as is (EmbeddedResource)
    assert isinstance(result[0], EmbeddedResource)

    mock_session.call_tool.return_value = CallToolResult(
        isError=True,
        content=[],
    )

    error_tool = tools[1]
    error_tool_type = BaseTool.type_from_base_model_type(error_tool)
    with pytest.raises(RuntimeError):
        await error_tool_type().call()  # pyright: ignore [reportAbstractUsage]
