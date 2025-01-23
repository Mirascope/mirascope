"""Tests the `openai.stream` module."""

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_chunk import (
    Choice as ChunkChoice,
)
from openai.types.chat.chat_completion_chunk import (
    ChoiceDelta,
    ChoiceDeltaToolCall,
    ChoiceDeltaToolCallFunction,
)
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from openai.types.completion_usage import CompletionUsage

from mirascope.core.openai.call_response import OpenAICallResponse
from mirascope.core.openai.call_response_chunk import OpenAICallResponseChunk
from mirascope.core.openai.stream import OpenAIStream
from mirascope.core.openai.tool import OpenAITool


def test_openai_stream() -> None:
    """Tests the `OpenAIStream` class."""
    assert OpenAIStream._provider == "openai"

    class FormatBook(OpenAITool):
        """Returns the title and author nicely formatted."""

        title: str
        author: str

        def call(self) -> None:
            """Dummy call."""

    tool_call_delta = ChoiceDeltaToolCall(
        index=0,
        id="id",
        function=ChoiceDeltaToolCallFunction(
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
            name="FormatBook",
        ),
        type="function",
    )
    usage = CompletionUsage(completion_tokens=1, prompt_tokens=1, total_tokens=2)
    chunks = [
        ChatCompletionChunk(
            id="id",
            choices=[
                ChunkChoice(
                    delta=ChoiceDelta(content="content", tool_calls=None), index=0
                )
            ],
            created=0,
            model="gpt-4o",
            object="chat.completion.chunk",
        ),
        ChatCompletionChunk(
            id="id",
            choices=[
                ChunkChoice(
                    delta=ChoiceDelta(
                        content=None,
                        tool_calls=[tool_call_delta],
                    ),
                    index=0,
                )
            ],
            created=0,
            model="gpt-4o",
            object="chat.completion.chunk",
            usage=usage,
        ),
    ]

    def generator():
        for chunk in chunks:
            call_response_chunk = OpenAICallResponseChunk(chunk=chunk)
            if tool_calls := call_response_chunk.chunk.choices[0].delta.tool_calls:
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

    stream = OpenAIStream(
        stream=generator(),
        metadata={},
        tool_types=[FormatBook],
        call_response_type=OpenAICallResponse,
        model="gpt-4o",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[{"role": "user", "content": "content"}],
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
    assert stream.cost == 1.25e-05

    format_book = FormatBook.from_tool_call(
        ChatCompletionMessageToolCall(
            id="id",
            function=Function(
                arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
                name="FormatBook",
            ),
            type="function",
        )
    )
    assert format_book.tool_call is not None
    assert stream.message_param == {
        "role": "assistant",
        "content": "content",
        "tool_calls": [format_book.tool_call.model_dump()],
    }


def test_construct_call_response() -> None:
    """Tests the `OpenAIStream.construct_call_response` method."""

    class FormatBook(OpenAITool):
        """Returns the title and author nicely formatted."""

        title: str
        author: str

        def call(self) -> None:
            """Dummy call."""

    tool_call = ChoiceDeltaToolCall(
        index=0,
        id="id",
        function=ChoiceDeltaToolCallFunction(
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
            name="FormatBook",
        ),
        type="function",
    )
    usage = CompletionUsage(completion_tokens=1, prompt_tokens=1, total_tokens=2)
    chunks = [
        ChatCompletionChunk(
            id="id",
            choices=[
                ChunkChoice(
                    delta=ChoiceDelta(content="content", tool_calls=None), index=0
                )
            ],
            created=0,
            model="gpt-4o",
            object="chat.completion.chunk",
        ),
        ChatCompletionChunk(
            id="id",
            choices=[
                ChunkChoice(
                    delta=ChoiceDelta(
                        content=None,
                        tool_calls=[tool_call],
                    ),
                    index=0,
                )
            ],
            created=0,
            model="gpt-4o",
            object="chat.completion.chunk",
            usage=usage,
        ),
    ]

    tool_call = None

    def generator():
        nonlocal tool_call
        for chunk in chunks:
            call_response_chunk = OpenAICallResponseChunk(chunk=chunk)
            if tool_calls := call_response_chunk.chunk.choices[0].delta.tool_calls:
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

    stream = OpenAIStream(
        stream=generator(),
        metadata={},
        tool_types=[FormatBook],
        call_response_type=OpenAICallResponse,
        model="gpt-4o",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[{"role": "user", "content": "content"}],
        call_params={},
        call_kwargs={},
    )

    for _ in stream:
        pass

    tool_call = ChatCompletionMessageToolCall(
        id="id",
        function=Function(
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
            name="FormatBook",
        ),
        type="function",
    )
    completion = ChatCompletion(
        id="id",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content="content", role="assistant", tool_calls=[tool_call]
                ),
            )
        ],
        created=0,
        model="gpt-4o",
        object="chat.completion",
        usage=usage,
    )
    call_response = OpenAICallResponse(
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


def test_construct_call_response_no_usage() -> None:
    """Tests the `OpenAIStream.construct_call_response` method with no usage."""
    chunks = [
        ChatCompletionChunk(
            id="id",
            choices=[
                ChunkChoice(
                    delta=ChoiceDelta(content="content", tool_calls=None), index=0
                )
            ],
            created=0,
            model="gpt-4o",
            object="chat.completion.chunk",
        ),
    ]

    def generator():
        for chunk in chunks:
            call_response_chunk = OpenAICallResponseChunk(chunk=chunk)
            yield call_response_chunk, None

    stream = OpenAIStream(
        stream=generator(),
        metadata={},
        tool_types=None,
        call_response_type=OpenAICallResponse,
        model="gpt-4o",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[{"role": "user", "content": "content"}],
        call_params={},
        call_kwargs={},
    )
    for _ in stream:
        pass
    constructed_call_response = stream.construct_call_response()
    assert constructed_call_response.usage is None


@pytest.mark.asyncio
async def test_openai_stream_audio() -> None:
    """Tests the `OpenAIStream` class with audio output."""
    chunks = [
        ChatCompletionChunk(
            id="id",
            choices=[
                ChunkChoice(
                    delta=ChoiceDelta(
                        content="content",
                        audio={"id": "audio-id-123"},  # pyright: ignore [reportCallIssue]
                    ),
                    index=0,
                )
            ],
            created=0,
            model="gpt-4o",
            object="chat.completion.chunk",
        ),
    ]

    def generator():
        for chunk in chunks:
            yield OpenAICallResponseChunk(chunk=chunk), None

    stream = OpenAIStream(
        stream=generator(),
        metadata={},
        tool_types=None,
        call_response_type=OpenAICallResponse,
        model="gpt-4o",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[{"role": "user", "content": "content"}],
        call_params={},
        call_kwargs={},
    )
    assert stream.audio_id is None

    for _ in stream:
        pass

    assert stream.audio_id == "audio-id-123"
    assert stream.message_param == {
        "role": "assistant",
        "content": "content",
        "audio": {"id": "audio-id-123"},
    }

    async def generator_async():
        for chunk in chunks:
            yield OpenAICallResponseChunk(chunk=chunk), None

    stream_async = OpenAIStream(
        stream=generator_async(),
        metadata={},
        tool_types=None,
        call_response_type=OpenAICallResponse,
        model="gpt-4o",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[{"role": "user", "content": "content"}],
        call_params={},
        call_kwargs={},
    )

    async for _ in stream_async:
        pass

    assert stream.audio_id == "audio-id-123"
    assert stream.message_param == {
        "role": "assistant",
        "content": "content",
        "audio": {"id": "audio-id-123"},
    }
