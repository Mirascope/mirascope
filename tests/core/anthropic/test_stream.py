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

    tool_call = ToolUseBlock(
        id="id",
        input={
            "tool_call": {
                "id": "1",
                "type": "tool_use",
                "name": "FormatBook",
                "input": {
                    "title": "Sapiens: A Brief History of Humankind",
                    "author": "Harari, Yuval Noah",
                },
            },
            "title": "Sapiens: A Brief History of Humankind",
            "author": "Harari, Yuval Noah",
        },
        name="FormatBook",
        type="tool_use",
    )
    chunks = [
        RawMessageStartEvent(
            message=Message(
                id="msg_01XRLekeRGvokAb5q5p7rSna",
                content=[],
                model="claude-3-5-sonnet-20240620",
                role="assistant",
                stop_reason=None,
                stop_sequence=None,
                type="message",
                usage=Usage(input_tokens=559, output_tokens=12),
            ),
            type="message_start",
        ),
        RawContentBlockStartEvent(
            content_block=ToolUseBlock(
                id="toolu_01U3cgdufZF6J6kxvbGxdq5L",
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
            delta=InputJsonDelta(partial_json='{"t', type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json="ool_ca", type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json='ll": {"id', type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json='": "1", "', type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json='name"', type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json=': "Form', type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json="at", type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json="Book", type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json='", "type": ', type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json='"too', type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json='l_use", "i', type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json="nput", type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json='": {"titl', type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json='e": "Sapiens', type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json=": A", type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json=" Brief Hi", type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json="story of Hu", type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json="mank", type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json='ind", ', type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json='"auth', type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json='or": "Ha', type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json="rari, Yu", type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json="val Noah", type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json='"}}', type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json=', "ti', type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json="tl", type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json='e": ', type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json='"Sapiens: ', type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json="A Bri", type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json="ef History", type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json=" of Humankin", type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json='d"', type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json=', "au', type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json='thor":', type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json=' "Ha', type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json="ra", type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json="ri, ", type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockDeltaEvent(
            delta=InputJsonDelta(partial_json='Yuval Noah"}', type="input_json_delta"),
            index=0,
            type="content_block_delta",
        ),
        RawContentBlockStopEvent(index=0, type="content_block_stop"),
        RawMessageDeltaEvent(
            delta=Delta(stop_reason="tool_use", stop_sequence=None),
            type="message_delta",
            usage=MessageDeltaUsage(output_tokens=162),
        ),
        RawMessageStopEvent(type="message_stop"),
    ]
    # chunks = [
    #     ChatCompletionChunk(
    #         id="id",
    #         choices=[
    #             Choice(delta=ChoiceDelta(content="content", tool_calls=None), index=0)
    #         ],
    #         created=0,
    #         model="gpt-4o",
    #         object="chat.completion.chunk",
    #     ),
    #     ChatCompletionChunk(
    #         id="id",
    #         choices=[
    #             Choice(
    #                 delta=ChoiceDelta(
    #                     content=None,
    #                     tool_calls=[tool_call],
    #                 ),
    #                 index=0,
    #             )
    #         ],
    #         created=0,
    #         model="gpt-4o",
    #         object="chat.completion.chunk",
    #         usage=usage,
    #     ),
    # ]

    tool_call = None

    def generator():
        nonlocal tool_call
        for chunk in chunks:
            call_response_chunk = AnthropicCallResponseChunk(chunk=chunk)
            if tool_calls := call_response_chunk.tool_calls:
                assert tool_calls[0].function
                tool_call = ChatCompletionMessageToolCall(
                    id="id",
                    function=Function(**tool_calls[0].function.model_dump()),
                    type="function",
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
    assert stream.cost == 2e-5
    assert stream.message_param == {
        "role": "assistant",
        "content": "content",
        "tool_calls": [tool_call],
    }
