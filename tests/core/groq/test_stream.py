"""Tests the `groq.stream` module."""

import pytest
from groq.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
)
from groq.types.chat.chat_completion import Choice
from groq.types.chat.chat_completion_chunk import (
    Choice as ChoiceChunk,
)
from groq.types.chat.chat_completion_chunk import (
    ChoiceDelta,
    ChoiceDeltaToolCall,
    ChoiceDeltaToolCallFunction,
)
from groq.types.chat.chat_completion_message import ChatCompletionMessage
from groq.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from groq.types.completion_usage import CompletionUsage

from mirascope.core.groq.call_response import GroqCallResponse
from mirascope.core.groq.call_response_chunk import GroqCallResponseChunk
from mirascope.core.groq.stream import GroqStream
from mirascope.core.groq.tool import GroqTool


def test_groq_stream() -> None:
    """Tests the `GroqStream` class."""
    assert GroqStream._provider == "groq"

    class FormatBook(GroqTool):
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
                ChoiceChunk(
                    delta=ChoiceDelta(content="content", tool_calls=None), index=0
                )
            ],
            created=0,
            model="llama3-70b-8192",
            object="chat.completion.chunk",
            x_groq=None,
        ),
        ChatCompletionChunk(
            id="id",
            choices=[
                ChoiceChunk(
                    delta=ChoiceDelta(
                        content=None,
                        tool_calls=[tool_call],
                    ),
                    index=0,
                )
            ],
            created=0,
            model="llama3-70b-8192",
            object="chat.completion.chunk",
            usage=usage,
            x_groq=None,
        ),
    ]

    tool_call = None

    def generator():
        nonlocal tool_call
        for chunk in chunks:
            call_response_chunk = GroqCallResponseChunk(chunk=chunk)
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

    stream = GroqStream(
        stream=generator(),
        metadata={},
        tool_types=[FormatBook],
        call_response_type=GroqCallResponse,
        model="llama3-70b-8192",
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
    assert stream.cost == 1.38e-6
    assert stream.message_param == {
        "role": "assistant",
        "content": "content",
        "tool_calls": [tool_call],
    }


def test_construct_call_response() -> None:
    """Tests the `GroqStream.construct_call_response` method."""

    class FormatBook(GroqTool):
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
                ChoiceChunk(
                    delta=ChoiceDelta(content="content", tool_calls=None), index=0
                )
            ],
            created=0,
            model="llama3-70b-8192",
            object="chat.completion.chunk",
            x_groq=None,
        ),
        ChatCompletionChunk(
            id="id",
            choices=[
                ChoiceChunk(
                    delta=ChoiceDelta(
                        content=None,
                        tool_calls=[tool_call],
                    ),
                    index=0,
                    finish_reason="stop",
                )
            ],
            created=0,
            model="llama3-70b-8192",
            object="chat.completion.chunk",
            usage=usage,
            x_groq=None,
        ),
    ]

    tool_call = None

    def generator():
        nonlocal tool_call
        for chunk in chunks:
            call_response_chunk = GroqCallResponseChunk(chunk=chunk)
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

    stream = GroqStream(
        stream=generator(),
        metadata={},
        tool_types=[FormatBook],
        call_response_type=GroqCallResponse,
        model="llama3-70b-8192",
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
        model="llama3-70b-8192",
        object="chat.completion",
        usage=usage,
    )
    call_response = GroqCallResponse(
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
    """Tests the `GroqStream.construct_call_response` method with no usage."""
    chunks = [
        ChatCompletionChunk(
            id="id",
            choices=[
                ChoiceChunk(
                    delta=ChoiceDelta(content="content", tool_calls=None), index=0
                )
            ],
            created=0,
            model="gpt-4o",
            object="chat.completion.chunk",
            x_groq=None,
        ),
    ]

    def generator():
        for chunk in chunks:
            call_response_chunk = GroqCallResponseChunk(chunk=chunk)
            yield call_response_chunk, None

    stream = GroqStream(
        stream=generator(),
        metadata={},
        tool_types=None,
        call_response_type=GroqCallResponse,
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
