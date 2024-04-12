"""A module for convenience around streaming tools with Anthropic.

NOTE: this feature is not officially supported by Anthropic. We're forcing it to output
JSON so that we can stream tools.
"""
from typing import AsyncGenerator, Generator, Literal, Optional, Type, overload

from anthropic.types.beta.tools import ToolUseBlock
from pydantic_core import from_json

from ..base.tool_streams import BaseToolStream
from ..partial import partial
from .tools import AnthropicTool
from .types import AnthropicCallResponseChunk


def _handle_chunk(
    buffer: str,
    chunk: AnthropicCallResponseChunk,
    current_tool_call: ToolUseBlock,
    current_tool_type: Optional[Type[AnthropicTool]],
    allow_partial: bool,
    num_open_parens: int,
) -> tuple[
    str,
    Optional[AnthropicTool],
    ToolUseBlock,
    Optional[Type[AnthropicTool]],
    int,
    bool,
]:
    """Handles a chunk of the stream."""
    if not chunk.tool_types:
        return (
            buffer,
            None,
            current_tool_call,
            current_tool_type,
            num_open_parens,
            False,
        )

    # NOTE: we're assuming JSON mode is active
    if chunk.response_format != "json":
        raise ValueError(
            "You must use `response_format='json' to stream tools with Anthropic."
        )

    if chunk_content := chunk.content:
        for i, char in enumerate(chunk_content):
            if char == "{":
                num_open_parens += 1
            if char == "}":
                num_open_parens -= 1
                if num_open_parens == 0:
                    buffer += chunk_content[: i + 1] if i < len(chunk_content) else ""
                    chunk_content = chunk_content[i + 1 :]
                    num_open_parens += chunk_content.count("{")
                    num_open_parens -= chunk_content.count("}")
                    current_tool_call.input = from_json(buffer)
                    # we have to type ignore since `input` is of type `object`
                    if "tool_name" not in current_tool_call.input:  # type: ignore
                        raise RuntimeError("No `tool_name` field for tool.")
                    tool_name = current_tool_call.input.pop("tool_name")  # type: ignore
                    for tool_type in chunk.tool_types:
                        if tool_type.__name__ == tool_name:
                            current_tool_type = tool_type
                            break
                    if current_tool_type is None:
                        raise RuntimeError("Unknown tool returned.")
                    return (
                        chunk_content,
                        current_tool_type.from_tool_call(current_tool_call),
                        current_tool_call,
                        None,
                        num_open_parens,
                        True,
                    )
        buffer += chunk_content

        if allow_partial:
            current_tool_call.input = from_json(buffer, allow_partial=True)
            # we have to type ignore since `input` is of type `object`
            if "tool_name" in current_tool_call.input:  # type: ignore
                tool_name = current_tool_call.input.pop("tool_name")  # type: ignore
                for tool_type in chunk.tool_types:
                    if tool_type.__name__ == tool_name:
                        current_tool_type = tool_type
                        break
                if current_tool_type is None:
                    raise RuntimeError("Unknown tool returned.")
            if current_tool_type is not None:
                return (
                    buffer,
                    partial(current_tool_type).from_tool_call(
                        ToolUseBlock(
                            id="id",
                            input=current_tool_call.input,
                            name=current_tool_type.__name__,
                            type="tool_use",
                        )
                    ),
                    current_tool_call,
                    current_tool_type,
                    num_open_parens,
                    False,
                )
    return buffer, None, current_tool_call, current_tool_type, num_open_parens, False


class AnthropicToolStream(BaseToolStream[AnthropicCallResponseChunk, AnthropicTool]):
    """A base class for streaming tools from response chunks."""

    @classmethod
    @overload
    def from_stream(
        cls,
        stream: Generator[AnthropicCallResponseChunk, None, None],
        allow_partial: Literal[True],
    ) -> Generator[Optional[AnthropicTool], None, None]:
        yield ...  # type: ignore  # pragma: no cover

    @classmethod
    @overload
    def from_stream(
        cls,
        stream: Generator[AnthropicCallResponseChunk, None, None],
        allow_partial: Literal[False],
    ) -> Generator[AnthropicTool, None, None]:
        yield ...  # type: ignore  # pragma: no cover

    @classmethod
    @overload
    def from_stream(
        cls,
        stream: Generator[AnthropicCallResponseChunk, None, None],
        allow_partial: bool = False,
    ) -> Generator[Optional[AnthropicTool], None, None]:
        yield ...  # type: ignore  # pragma: no cover

    @classmethod
    def from_stream(cls, stream, allow_partial=False):
        """Yields partial tools from the given stream of chunks.

        Args:
            stream: The generator of chunks from which to stream tools.
            allow_partial: Whether to allow partial tools.

        Raises:
            RuntimeError: if a tool in the stream is of an unknown type.
        """
        cls._check_version_for_partial(allow_partial)
        current_tool_call = ToolUseBlock(id="", input={}, name="", type="tool_use")
        current_tool_type = None
        buffer, num_open_parens = "{", 1
        for chunk in stream:
            if chunk.type == "message_start":
                current_tool_call.id = chunk.chunk.message.id
                continue
            (
                buffer,
                tool,
                current_tool_call,
                current_tool_type,
                num_open_parens,
                starting_new,
            ) = _handle_chunk(
                buffer,
                chunk,
                current_tool_call,
                current_tool_type,
                allow_partial,
                num_open_parens,
            )
            if tool is not None:
                yield tool
            if starting_new:
                yield None

    @classmethod
    @overload
    async def from_async_stream(
        cls,
        stream: AsyncGenerator[AnthropicCallResponseChunk, None],
        allow_partial: Literal[True],
    ) -> AsyncGenerator[Optional[AnthropicTool], None]:
        yield ...  # type: ignore  # pragma: no cover

    @classmethod
    @overload
    async def from_async_stream(
        cls,
        stream: AsyncGenerator[AnthropicCallResponseChunk, None],
        allow_partial: Literal[False],
    ) -> AsyncGenerator[AnthropicTool, None]:
        yield ...  # type: ignore  # pragma: no cover

    @classmethod
    @overload
    async def from_async_stream(
        cls,
        stream: AsyncGenerator[AnthropicCallResponseChunk, None],
        allow_partial: bool = False,
    ) -> AsyncGenerator[Optional[AnthropicTool], None]:
        yield ...  # type: ignore  # pragma: no cover

    @classmethod
    async def from_async_stream(cls, async_stream, allow_partial=False):
        """Yields partial tools from the given stream of chunks asynchronously.

        Args:
            stream: The async generator of chunks from which to stream tools.
            allow_partial: Whether to allow partial tools.

        Raises:
            RuntimeError: if a tool in the stream is of an unknown type.
        """
        cls._check_version_for_partial(allow_partial)
        current_tool_call = ToolUseBlock(id="", input={}, name="", type="tool_use")
        current_tool_type = None
        buffer, num_open_parens = "{", 1
        async for chunk in async_stream:
            if chunk.type == "message_start":
                current_tool_call.id = chunk.chunk.message.id
                continue
            (
                buffer,
                tool,
                current_tool_call,
                current_tool_type,
                num_open_parens,
                starting_new,
            ) = _handle_chunk(
                buffer,
                chunk,
                current_tool_call,
                current_tool_type,
                allow_partial,
                num_open_parens,
            )
            if tool is not None:
                yield tool
            if starting_new:
                yield None
