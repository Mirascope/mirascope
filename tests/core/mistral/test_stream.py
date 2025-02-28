"""Tests the `mistral.stream` module."""

import pytest
from mistralai import AssistantMessage
from mistralai.models import (
    ChatCompletionChoice,
    ChatCompletionResponse,
    CompletionChunk,
    CompletionResponseStreamChoice,
    DeltaMessage,
    FunctionCall,
    ToolCall,
    UsageInfo,
)

from mirascope.core.mistral.call_response import MistralCallResponse
from mirascope.core.mistral.call_response_chunk import MistralCallResponseChunk
from mirascope.core.mistral.stream import MistralStream
from mirascope.core.mistral.tool import MistralTool


def test_mistral_stream() -> None:
    """Tests the `MistralStream` class."""
    assert MistralStream._provider == "mistral"

    class FormatBook(MistralTool):
        """Returns the title and author nicely formatted."""

        title: str
        author: str

        def call(self) -> None:
            """Dummy call."""

    tool_call_delta = ToolCall(
        id="id",
        function=FunctionCall(
            name="FormatBook",
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
        ),
        type="function",
    )
    usage = UsageInfo(prompt_tokens=1, completion_tokens=1, total_tokens=2)
    chunks = [
        CompletionChunk(
            id="id",
            choices=[
                CompletionResponseStreamChoice(
                    delta=DeltaMessage(content="content", tool_calls=None),
                    index=0,
                    finish_reason=None,
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
        ),
        CompletionChunk(
            id="id",
            choices=[
                CompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(
                        content=None,
                        tool_calls=[tool_call_delta],
                    ),
                    finish_reason=None,
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
            usage=usage,
        ),
    ]

    def generator():
        for chunk in chunks:
            call_response_chunk = MistralCallResponseChunk(chunk=chunk)
            if tool_calls := call_response_chunk.chunk.choices[0].delta.tool_calls:
                assert tool_calls[0].function
                tool_call = ToolCall(
                    id="id",
                    function=FunctionCall(**tool_calls[0].function.model_dump()),
                    type="function",
                )
                yield (
                    call_response_chunk,
                    FormatBook.from_tool_call(tool_call),
                )
            else:
                yield call_response_chunk, None

    stream = MistralStream(
        stream=generator(),
        metadata={},
        tool_types=[FormatBook],
        call_response_type=MistralCallResponse,
        model="mistral-large-latest",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
    )

    with pytest.raises(
        ValueError, match="No stream response, check if the stream has been consumed."
    ):
        stream.construct_call_response()

    assert stream.cost is None
    for _ in stream:
        pass
    assert stream.cost == 8e-06

    format_book = FormatBook.from_tool_call(
        ToolCall(
            id="id",
            function=FunctionCall(
                name="FormatBook",
                arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
            ),
            type="function",
        )
    )
    assert format_book.tool_call is not None
    assert stream.message_param == AssistantMessage(
        content="content",
        tool_calls=[format_book.tool_call],
    )


def test_construct_call_response() -> None:
    class FormatBook(MistralTool):
        """Returns the title and author nicely formatted."""

        title: str
        author: str

        def call(self) -> None:
            """Dummy call."""

    tool_call_delta = ToolCall(
        id="id",
        function=FunctionCall(
            name="FormatBook",
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
        ),
        type="function",
    )
    usage = UsageInfo(prompt_tokens=1, completion_tokens=1, total_tokens=2)
    chunks = [
        CompletionChunk(
            id="id",
            choices=[
                CompletionResponseStreamChoice(
                    delta=DeltaMessage(content="content", tool_calls=None),
                    index=0,
                    finish_reason=None,
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
        ),
        CompletionChunk(
            id="id",
            choices=[
                CompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(
                        content=None,
                        tool_calls=[tool_call_delta],
                    ),
                    finish_reason="stop",
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
            usage=usage,
        ),
    ]

    def generator():
        for chunk in chunks:
            call_response_chunk = MistralCallResponseChunk(chunk=chunk)
            if tool_calls := call_response_chunk.chunk.choices[0].delta.tool_calls:
                assert tool_calls[0].function
                tool_call = ToolCall(
                    id="id",
                    function=FunctionCall(**tool_calls[0].function.model_dump()),
                    type="function",
                )
                yield (
                    call_response_chunk,
                    FormatBook.from_tool_call(tool_call),
                )
            else:
                yield call_response_chunk, None

    stream = MistralStream(
        stream=generator(),
        metadata={},
        tool_types=[FormatBook],
        call_response_type=MistralCallResponse,
        model="mistral-large-latest",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
    )

    for _ in stream:
        pass

    tool_call = ToolCall(
        id="id",
        function=FunctionCall(
            name="FormatBook",
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
        ),
        type="function",
    )
    completion = ChatCompletionResponse(
        id="id",
        choices=[
            ChatCompletionChoice(
                finish_reason="stop",
                index=0,
                message=AssistantMessage(content="content", tool_calls=[tool_call]),
            )
        ],
        created=0,
        model="mistral-large-latest",
        object="",
        usage=UsageInfo(prompt_tokens=1, completion_tokens=1, total_tokens=2),
    )
    call_response = MistralCallResponse(
        metadata={},
        response=completion,
        tool_types=[FormatBook],
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )
    constructed_call_response = stream.construct_call_response()
    assert constructed_call_response.response == call_response.response
