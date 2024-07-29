"""Tests the `anthropic.stream` module."""

from anthropic.types import (
    InputJsonDelta,
    Message,
    MessageDeltaUsage,
    RawContentBlockDeltaEvent,
    RawContentBlockStartEvent,
    RawContentBlockStopEvent,
    RawMessageDeltaEvent,
    RawMessageStartEvent,
    RawMessageStopEvent,
    ToolUseBlock,
    Usage,
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

        def call(self):
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
            delta=InputJsonDelta(partial_json="", type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(
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
    assert stream.cost is None
    for _ in stream:
        pass
    assert stream.cost == 3.3e-05
    assert stream.message_param == {
        "role": "assistant",
        "content": [
            ToolUseBlock(
                id="tool_id",
                input={
                    "title": "Sapiens: A Brief History of Humankind",
                    "author": "Harari, Yuval Noah",
                },
                name="FormatBook",
                type="tool_use",
            )
        ],
    }
