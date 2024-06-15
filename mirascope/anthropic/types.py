"""Type classes for interacting with Anthropics's Claude API."""

import json
from collections.abc import AsyncGenerator, Generator
from typing import Any, Literal, Optional, Type, Union, overload

from anthropic._types import Body, Headers, Query
from anthropic.lib.streaming import MessageStreamEvent
from anthropic.types import (
    ContentBlockDeltaEvent,
    ContentBlockStartEvent,
    Message,
    MessageParam,
    MessageStartEvent,
    TextBlock,
    TextDelta,
    ToolResultBlockParam,
    ToolUseBlock,
    Usage,
)
from anthropic.types.completion_create_params import Metadata
from httpx import Timeout
from pydantic import ConfigDict
from pydantic_core import from_json

from ..base.types import (
    BaseAsyncStream,
    BaseCallParams,
    BaseCallResponse,
    BaseCallResponseChunk,
    BaseStream,
    BaseToolStream,
)
from ..partial import partial
from .tools import AnthropicTool


class AnthropicCallParams(BaseCallParams[AnthropicTool]):
    """The parameters to use when calling d Claud API with a prompt.

    Example:

    ```python
    from mirascope.anthropic import AnthropicCall, AnthropicCallParams


    class BookRecommender(AnthropicCall):
        prompt_template = "Please recommend some books."

        call_params = AnthropicCallParams(
            model="anthropic-3-opus-20240229",
        )
    ```
    """

    max_tokens: int = 1000
    model: str = "claude-3-haiku-20240307"
    metadata: Optional[Metadata] = None
    stop_sequences: Optional[list[str]] = None
    system: Optional[str] = None
    temperature: Optional[float] = None
    top_k: Optional[int] = None
    top_p: Optional[float] = None
    extra_headers: Optional[Headers] = None
    extra_query: Optional[Query] = None
    extra_body: Optional[Body] = None
    timeout: Optional[Union[float, Timeout]] = 600

    response_format: Optional[Literal["json"]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def kwargs(
        self,
        tool_type: Optional[Type[AnthropicTool]] = None,
        exclude: Optional[set[str]] = None,
    ) -> dict[str, Any]:
        """Returns the keyword argument call parameters."""
        extra_exclude = {"response_format"}
        exclude = extra_exclude if exclude is None else exclude.union(extra_exclude)
        return super().kwargs(tool_type, exclude)


class AnthropicCallResponse(BaseCallResponse[Message, AnthropicTool]):
    """Convenience wrapper around the Anthropic Claude API.

    When using Mirascope's convenience wrappers to interact with Anthropic models via
    `AnthropicCall`, responses using `Anthropic.call()` will return an
    `AnthropicCallResponse`, whereby the implemented properties allow for simpler syntax
    and a convenient developer experience.

    Example:

    ```python
    from mirascope.anthropic import AnthropicCall


    class BookRecommender(AnthropicCall):
        prompt_template = "Please recommend some books."


    print(BookRecommender().call())
    ```
    """

    response_format: Optional[Literal["json"]] = None
    user_message_param: Optional[MessageParam] = None

    @property
    def message_param(self) -> MessageParam:
        """Returns the assistant's response as a message parameter."""
        return self.response.model_dump(include={"content", "role"})  # type: ignore

    @property
    def tools(self) -> Optional[list[AnthropicTool]]:
        """Returns the tools for the 0th choice message."""
        if not self.tool_types:
            return None

        if self.response_format == "json":
            # Note: we only handle single tool calls in JSON mode.
            tool_type = self.tool_types[0]
            return [
                tool_type.from_tool_call(
                    ToolUseBlock(
                        id="id",
                        input=json.loads(self.content),
                        name=tool_type.name(),
                        type="tool_use",
                    )
                )
            ]

        if self.response.stop_reason != "tool_use":
            raise RuntimeError(
                "Generation stopped with stop reason that is not `tool_use`. "
                "This is likely due to a limit on output tokens that is too low. "
                "Note that this could also indicate no tool is beind called, so we "
                "recommend that you check the output of the call to confirm. "
                f"Stop Reason: {self.response.stop_reason} "
            )

        extracted_tools = []
        for tool_call in self.response.content:
            if tool_call.type != "tool_use":
                continue
            for tool_type in self.tool_types:
                if tool_call.name == tool_type.name():
                    tool = tool_type.from_tool_call(tool_call)
                    extracted_tools.append(tool)
                    break

        return extracted_tools

    @property
    def tool(self) -> Optional[AnthropicTool]:
        """Returns the 0th tool for the 0th choice text block."""
        tools = self.tools
        if tools:
            return tools[0]
        return None

    @classmethod
    def tool_message_params(
        self, tools_and_outputs: list[tuple[AnthropicTool, str]]
    ) -> list[MessageParam]:
        """Returns the tool message parameters for tool call results."""
        return [
            {
                "role": "user",
                "content": [
                    ToolResultBlockParam(
                        tool_use_id=tool.tool_call.id,
                        type="tool_result",
                        content=[{"text": output, "type": "text"}],
                    )
                    for tool, output in tools_and_outputs
                ],
            }
        ]

    @property
    def content(self) -> str:
        """Returns the string text of the 0th text block."""
        block = self.response.content[0]
        return block.text if block.type == "text" else ""

    @property
    def model(self) -> str:
        """Returns the name of the response model."""
        return self.response.model

    @property
    def id(self) -> str:
        """Returns the id of the response."""
        return self.response.id

    @property
    def finish_reasons(self) -> Optional[list[str]]:
        """Returns the finish reason of the response."""
        return [str(self.response.stop_reason)]

    @property
    def usage(self) -> Usage:
        """Returns the usage of the message."""
        return self.response.usage

    @property
    def input_tokens(self) -> int:
        """Returns the number of input tokens."""
        return self.usage.input_tokens

    @property
    def output_tokens(self) -> int:
        """Returns the number of output tokens."""
        return self.usage.output_tokens

    def dump(self) -> dict[str, Any]:
        """Dumps the response to a dictionary."""
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "output": self.response.model_dump(),
        }


class AnthropicCallResponseChunk(
    BaseCallResponseChunk[MessageStreamEvent, AnthropicTool]
):
    """Convenience wrapper around the Anthropic API streaming chunks.

    When using Mirascope's convenience wrappers to interact with Anthropic models via
    `AnthropicCall`, responses using `AnthropicCall.stream()` will yield
    `AnthropicCallResponseChunk`, whereby the implemented properties allow for simpler
    syntax and a convenient developer experience.

    Example:

    ```python
    from mirascope.anthropic import AnthropicCall


    class Math(AnthropicCall):
        prompt_template = "What is 1 + 2?"


    content = ""
    for chunk in Math().stream():
        content += chunk.content
        print(content)
    #> 1
    #  1 +
    #  1 + 2
    #  1 + 2 equals
    #  1 + 2 equals
    #  1 + 2 equals 3
    #  1 + 2 equals 3.
    ```
    """

    response_format: Optional[Literal["json"]] = None
    user_message_param: Optional[MessageParam] = None

    @property
    def type(
        self,
    ) -> Literal[
        "text",
        "input_json",
        "message_start",
        "message_delta",
        "message_stop",
        "content_block_start",
        "content_block_delta",
        "content_block_stop",
    ]:
        """Returns the type of the chunk."""
        return self.chunk.type

    @property
    def content(self) -> str:
        """Returns the string content of the 0th message."""
        if isinstance(self.chunk, ContentBlockStartEvent):
            return (
                self.chunk.content_block.text
                if isinstance(self.chunk.content_block, TextBlock)
                else ""
            )
        if isinstance(self.chunk, ContentBlockDeltaEvent):
            return (
                self.chunk.delta.text if isinstance(self.chunk.delta, TextDelta) else ""
            )
        return ""

    @property
    def model(self) -> Optional[str]:
        """Returns the name of the response model."""
        if isinstance(self.chunk, MessageStartEvent):
            return self.chunk.message.model
        return None

    @property
    def id(self) -> Optional[str]:
        """Returns the id of the response."""
        if isinstance(self.chunk, MessageStartEvent):
            return self.chunk.message.id
        return None

    @property
    def finish_reasons(self) -> Optional[list[str]]:
        """Returns the finish reason of the response."""
        if isinstance(self.chunk, MessageStartEvent):
            return [str(self.chunk.message.stop_reason)]
        return None

    @property
    def usage(self) -> Optional[Usage]:
        """Returns the usage of the message."""
        if isinstance(self.chunk, MessageStartEvent):
            return self.chunk.message.usage
        return None

    @property
    def input_tokens(self) -> Optional[int]:
        """Returns the number of input tokens."""
        if self.usage:
            return self.usage.input_tokens
        return None

    @property
    def output_tokens(self) -> Optional[int]:
        """Returns the number of output tokens."""
        if self.usage:
            return self.usage.output_tokens
        return None


def _handle_chunk(
    buffer: str,
    chunk: AnthropicCallResponseChunk,
    current_tool_call: ToolUseBlock,
    current_tool_type: Optional[Type[AnthropicTool]],
    allow_partial: bool,
) -> tuple[
    str,
    Optional[AnthropicTool],
    ToolUseBlock,
    Optional[Type[AnthropicTool]],
    bool,
]:
    """Handles a chunk of the stream."""
    if not chunk.tool_types:
        return (
            buffer,
            None,
            current_tool_call,
            current_tool_type,
            False,
        )

    if chunk.chunk.type == "content_block_stop" and isinstance(
        chunk.chunk.content_block, ToolUseBlock
    ):
        content_block = chunk.chunk.content_block
        current_tool_call.input = from_json(buffer)
        return (
            buffer,
            current_tool_type.from_tool_call(current_tool_call)
            if current_tool_type
            else None,
            ToolUseBlock(id="", input={}, name="", type="tool_use"),
            None,
            False,
        )

    # Reset on new tool
    if chunk.chunk.type == "content_block_start" and isinstance(
        chunk.chunk.content_block, ToolUseBlock
    ):
        content_block = chunk.chunk.content_block
        current_tool_type = None
        for tool_type in chunk.tool_types:
            if tool_type.name() == content_block.name:
                current_tool_type = tool_type
                break
        if current_tool_type is None:
            raise RuntimeError(f"Unknown tool type in stream: {content_block.name}.")
        return (
            "",
            None,
            ToolUseBlock(
                id=content_block.id, input={}, name=content_block.name, type="tool_use"
            ),
            current_tool_type,
            bool(buffer),
        )

    # Update arguments with each chunk
    if chunk.chunk.type == "input_json":
        buffer += chunk.chunk.partial_json

        if allow_partial and current_tool_type:
            current_tool_call.input = from_json(buffer, allow_partial=True)
            return (
                buffer,
                partial(current_tool_type).from_tool_call(current_tool_call),
                current_tool_call,
                current_tool_type,
                False,
            )

    return buffer, None, current_tool_call, current_tool_type, False


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
        buffer = ""
        for chunk in stream:
            (
                buffer,
                tool,
                current_tool_call,
                current_tool_type,
                starting_new,
            ) = _handle_chunk(
                buffer,
                chunk,
                current_tool_call,
                current_tool_type,
                allow_partial,
            )
            if tool is not None:
                yield tool
            if starting_new and allow_partial:
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
        buffer = ""
        async for chunk in async_stream:
            (
                buffer,
                tool,
                current_tool_call,
                current_tool_type,
                starting_new,
            ) = _handle_chunk(
                buffer,
                chunk,
                current_tool_call,
                current_tool_type,
                allow_partial,
            )
            if tool is not None:
                yield tool
            if starting_new and allow_partial:
                yield None


class AnthropicStream(
    BaseStream[
        AnthropicCallResponseChunk,
        MessageParam,
        MessageParam,
        AnthropicTool,
    ]
):
    """A class for streaming responses from Anthropic's Claude API."""

    def __init__(
        self,
        stream: Generator[AnthropicCallResponseChunk, None, None],
        allow_partial: bool = False,
    ):
        """Initializes an instance of `AnthropicStream`."""
        AnthropicToolStream._check_version_for_partial(allow_partial)
        super().__init__(stream, MessageParam)
        self._allow_partial = allow_partial

    def __iter__(
        self,
    ) -> Generator[
        tuple[AnthropicCallResponseChunk, Optional[AnthropicTool]], None, None
    ]:
        """Iterator over the stream and constructs tools as they are streamed."""
        current_tool_call = ToolUseBlock(id="", input={}, name="", type="tool_use")
        current_tool_type = None
        buffer, content = "", []
        for chunk, _ in super().__iter__():
            (
                buffer,
                tool,
                current_tool_call,
                current_tool_type,
                starting_new,
            ) = _handle_chunk(
                buffer,
                chunk,
                current_tool_call,
                current_tool_type,
                self._allow_partial,
            )
            if tool is not None:
                yield chunk, tool
            elif current_tool_type is None:
                yield chunk, None
            if starting_new and self._allow_partial:
                yield chunk, None
            if chunk.chunk.type == "content_block_stop":
                content.append(chunk.chunk.content_block.model_dump())
        if content:
            self.message_param["content"] = content  # type: ignore

    @classmethod
    def tool_message_params(cls, tools_and_outputs: list[tuple[AnthropicTool, str]]):
        """Returns the tool message parameters for tool call results."""
        return AnthropicCallResponse.tool_message_params(tools_and_outputs)


class AnthropicAsyncStream(
    BaseAsyncStream[
        AnthropicCallResponseChunk,
        MessageParam,
        MessageParam,
        AnthropicTool,
    ]
):
    """A class for streaming responses from Anthropic's Claude API."""

    def __init__(
        self,
        stream: AsyncGenerator[AnthropicCallResponseChunk, None],
        allow_partial: bool = False,
    ):
        """Initializes an instance of `AnthropicAsyncStream`."""
        AnthropicToolStream._check_version_for_partial(allow_partial)
        super().__init__(stream, MessageParam)
        self._allow_partial = allow_partial

    def __aiter__(
        self,
    ) -> AsyncGenerator[
        tuple[AnthropicCallResponseChunk, Optional[AnthropicTool]], None
    ]:
        """Async iterator over the stream and constructs tools as they are streamed."""
        stream = super().__aiter__()

        async def generator():
            current_tool_call = ToolUseBlock(id="", input={}, name="", type="tool_use")
            current_tool_type = None
            buffer, content = "", []
            async for chunk, _ in stream:
                (
                    buffer,
                    tool,
                    current_tool_call,
                    current_tool_type,
                    starting_new,
                ) = _handle_chunk(
                    buffer,
                    chunk,
                    current_tool_call,
                    current_tool_type,
                    self._allow_partial,
                )
                if tool is not None:
                    yield chunk, tool
                elif current_tool_type is None:
                    yield chunk, None
                if starting_new and self._allow_partial:
                    yield chunk, None
                if chunk.chunk.type == "content_block_stop":
                    content.append(chunk.chunk.content_block.model_dump())
            if content:
                self.message_param["content"] = content  # type: ignore

        return generator()

    @classmethod
    def tool_message_params(cls, tools_and_outputs: list[tuple[AnthropicTool, str]]):
        """Returns the tool message parameters for tool call results."""
        return AnthropicCallResponse.tool_message_params(tools_and_outputs)
