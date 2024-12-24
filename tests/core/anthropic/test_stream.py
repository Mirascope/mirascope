"""Tests the `anthropic.stream` module."""

import pytest
from anthropic.types import (
    Message,
    MessageDeltaUsage,
    RawContentBlockDeltaEvent,
    RawContentBlockStartEvent,
    RawContentBlockStopEvent,
    RawMessageDeltaEvent,
    RawMessageStartEvent,
    RawMessageStopEvent,
    TextBlock,
    TextDelta,
    ToolUseBlock,
    Usage,
)

try:
    from anthropic.types import (
        InputJsonDelta as InputJSONDelta,  # pyright: ignore [reportAttributeAccessIssue]
    )
except ImportError:
    from anthropic.types import (
        InputJSONDelta,  # pyright: ignore [reportAttributeAccessIssue]
    )

from anthropic.types.raw_message_delta_event import Delta

from mirascope.core.anthropic.call_params import AnthropicCallParams
from mirascope.core.anthropic.call_response import AnthropicCallResponse
from mirascope.core.anthropic.call_response_chunk import AnthropicCallResponseChunk
from mirascope.core.anthropic.stream import AnthropicStream
from mirascope.core.anthropic.tool import AnthropicTool


def test_anthropic_stream() -> None:
    """Tests the `AnthropicStream` class."""
    assert AnthropicStream._provider == "anthropic"

    class FormatBook(AnthropicTool):
        """Returns the title and author nicely formatted."""

        title: str
        author: str

        def call(self) -> None:
            """Dummy call."""

    chunks = [
        RawMessageStartEvent(
            message=Message(
                id="id",
                content=[],
                model="claude-3-5-sonnet-20240620",
                role="assistant",
                stop_reason=None,
                stop_sequence=None,
                type="message",
                usage=Usage(input_tokens=1, output_tokens=1),
            ),
            type="message_start",
        ),
        RawContentBlockStartEvent(
            content_block=ToolUseBlock(
                id="tool_id",
                input={},
                name="FormatBook",
                type="tool_use",
            ),
            index=0,
            type="content_block_start",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJSONDelta(partial_json="", type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJSONDelta(
                partial_json='{"'
                'title": "Sapiens: A Brief History of Humankind", '
                '"author": "Harari, Yuval Noah"}',
                type="input_json_delta",
            ),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockStopEvent(index=0, type="content_block_stop"),
        RawMessageDeltaEvent(
            delta=Delta(stop_reason="tool_use", stop_sequence=None),
            type="message_delta",
            usage=MessageDeltaUsage(output_tokens=1),
        ),
        RawMessageStopEvent(type="message_stop"),
    ]

    def generator():
        for chunk in chunks:
            call_response_chunk = AnthropicCallResponseChunk(chunk=chunk)
            if isinstance(call_response_chunk.chunk, RawContentBlockStartEvent) and (
                tool_call := call_response_chunk.chunk.content_block
            ):
                tool_call = ToolUseBlock(
                    id="tool_id",
                    input={
                        "title": "Sapiens: A Brief History of Humankind",
                        "author": "Harari, Yuval Noah",
                    },
                    name="FormatBook",
                    type="tool_use",
                )
                yield (
                    call_response_chunk,
                    FormatBook.from_tool_call(tool_call),
                )
            else:
                yield call_response_chunk, None

    stream = AnthropicStream(
        stream=generator(),
        metadata={},
        tool_types=[FormatBook],
        call_response_type=AnthropicCallResponse,
        model="claude-3-5-sonnet-20240620",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[{"role": "user", "content": "content"}],
        call_params=AnthropicCallParams(max_tokens=1000),
        call_kwargs={},
    )

    with pytest.raises(
        ValueError, match="No stream response, check if the stream has been consumed."
    ):
        stream.construct_call_response()

    assert stream.cost is None
    for _ in stream:
        pass
    assert stream.cost == 3.3e-05

    format_book = FormatBook.from_tool_call(
        ToolUseBlock(
            id="tool_id",
            input={
                "title": "Sapiens: A Brief History of Humankind",
                "author": "Harari, Yuval Noah",
            },
            name="FormatBook",
            type="tool_use",
        )
    )
    assert format_book.tool_call is not None
    assert stream.message_param == {
        "role": "assistant",
        "content": [format_book.tool_call.model_dump()],
    }


def test_construct_call_response() -> None:
    class FormatBook(AnthropicTool):
        """Returns the title and author nicely formatted."""

        title: str
        author: str

        def call(self) -> None:
            """Dummy call."""

    chunks = [
        RawMessageStartEvent(
            message=Message(
                id="id",
                content=[],
                model="claude-3-5-sonnet-20240620",
                role="assistant",
                stop_reason="end_turn",
                stop_sequence=None,
                type="message",
                usage=Usage(input_tokens=1, output_tokens=1),
            ),
            type="message_start",
        ),
        RawContentBlockStartEvent(
            content_block=ToolUseBlock(
                id="tool_id",
                input={},
                name="FormatBook",
                type="tool_use",
            ),
            index=0,
            type="content_block_start",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJSONDelta(partial_json="", type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJSONDelta(
                partial_json='{"'
                'title": "Sapiens: A Brief History of Humankind", '
                '"author": "Harari, Yuval Noah"}',
                type="input_json_delta",
            ),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockStopEvent(index=0, type="content_block_stop"),
        RawContentBlockStartEvent(
            content_block=TextBlock(text="", type="text"),
            index=1,
            type="content_block_start",
        ),
        RawContentBlockDeltaEvent(
            delta=TextDelta(text="content", type="text_delta"),
            index=1,
            type="content_block_delta",
        ),
        RawContentBlockStopEvent(index=1, type="content_block_stop"),
        RawMessageDeltaEvent(
            delta=Delta(stop_reason="tool_use", stop_sequence=None),
            type="message_delta",
            usage=MessageDeltaUsage(output_tokens=1),
        ),
        RawMessageStopEvent(type="message_stop"),
    ]

    def generator():
        for chunk in chunks:
            call_response_chunk = AnthropicCallResponseChunk(chunk=chunk)
            if (
                isinstance(call_response_chunk.chunk, RawContentBlockStartEvent)
                and (tool_call := call_response_chunk.chunk.content_block)
                and tool_call.type == "tool_use"
            ):
                tool_call = ToolUseBlock(
                    id="tool_id",
                    input={
                        "title": "Sapiens: A Brief History of Humankind",
                        "author": "Harari, Yuval Noah",
                    },
                    name="FormatBook",
                    type="tool_use",
                )
                yield (
                    call_response_chunk,
                    FormatBook.from_tool_call(tool_call),
                )
            else:
                yield call_response_chunk, None

    stream = AnthropicStream(
        stream=generator(),
        metadata={},
        tool_types=[FormatBook],
        call_response_type=AnthropicCallResponse,
        model="claude-3-5-sonnet-20240620",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[{"role": "user", "content": "content"}],
        call_params=AnthropicCallParams(max_tokens=1000),
        call_kwargs={},
    )

    for _ in stream:
        pass

    tool_call = ToolUseBlock(
        id="tool_id",
        input={
            "title": "Sapiens: A Brief History of Humankind",
            "author": "Harari, Yuval Noah",
        },
        name="FormatBook",
        type="tool_use",
    )
    content = TextBlock(text="content", type="text")
    completion = Message(
        id="id",
        content=[content, tool_call],
        model="claude-3-5-sonnet-20240620",
        role="assistant",
        stop_reason="end_turn",
        stop_sequence=None,
        type="message",
        usage=Usage(input_tokens=1, output_tokens=2),
    )
    call_response = AnthropicCallResponse(
        metadata={},
        response=completion,
        tool_types=[FormatBook],
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params=AnthropicCallParams(max_tokens=1000),
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )
    constructed_call_response = stream.construct_call_response()
    assert constructed_call_response.response == call_response.response


def test_construct_call_response_string_content() -> None:
    """Tests the `construct_call_response` method handles string message_param.
    This should never occur since we convert all string message_param to TextBlock.
    """
    chunks = [
        RawMessageStartEvent(
            message=Message(
                id="id",
                content=[],
                model="claude-3-5-sonnet-20240620",
                role="assistant",
                stop_reason="end_turn",
                stop_sequence=None,
                type="message",
                usage=Usage(input_tokens=1, output_tokens=1),
            ),
            type="message_start",
        )
    ]

    def generator():  # pragma: no cover
        for chunk in chunks:
            call_response_chunk = AnthropicCallResponseChunk(chunk=chunk)
            yield call_response_chunk, None

    stream = AnthropicStream(
        stream=generator(),
        metadata={},
        tool_types=None,
        call_response_type=AnthropicCallResponse,
        model="claude-3-5-sonnet-20240620",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[{"role": "user", "content": "content"}],
        call_params=AnthropicCallParams(max_tokens=1000),
        call_kwargs={},
    )
    stream.message_param = {
        "role": "assistant",
        "content": "content",
    }
    constructed_call_response = stream.construct_call_response()
    assert constructed_call_response.message_param == {
        "role": "assistant",
        "content": [{"text": "content", "type": "text"}],
    }
