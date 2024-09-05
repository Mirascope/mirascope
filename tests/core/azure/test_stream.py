"""Tests the `azure.stream` module."""

from datetime import datetime

import pytest
from azure.ai.inference.models import (
    ChatChoice,
    ChatCompletions,
    ChatCompletionsToolCall,
    ChatRequestMessage,
    ChatResponseMessage,
    CompletionsFinishReason,
    CompletionsUsage,
    FunctionCall,
    StreamingChatChoiceUpdate,
    StreamingChatCompletionsUpdate,
    StreamingChatResponseMessageUpdate,
    StreamingChatResponseToolCallUpdate,
    UserMessage,
)

from mirascope.core.azure.call_response import AzureCallResponse
from mirascope.core.azure.call_response_chunk import AzureCallResponseChunk
from mirascope.core.azure.stream import AzureStream
from mirascope.core.azure.tool import AzureTool


@pytest.fixture
def mock_datetime_now(monkeypatch):
    class MockDatetime:
        @classmethod
        def now(cls):
            return datetime.fromtimestamp(0)

    monkeypatch.setattr("datetime.datetime", MockDatetime)
    yield

    monkeypatch.undo()


def test_azure_stream() -> None:
    """Tests the `AzureStream` class."""
    assert AzureStream._provider == "azure"

    class FormatBook(AzureTool):
        """Returns the title and author nicely formatted."""

        title: str
        author: str

        def call(self) -> None:
            """Dummy call."""

    tool_call_delta = StreamingChatResponseToolCallUpdate(
        id="id",
        function=FunctionCall(
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
            name="FormatBook",
        ),
    )
    created = datetime.fromtimestamp(0)
    usage = CompletionsUsage(completion_tokens=1, prompt_tokens=1, total_tokens=2)
    chunks = [
        StreamingChatCompletionsUpdate(
            id="id",
            choices=[
                StreamingChatChoiceUpdate(
                    delta=StreamingChatResponseMessageUpdate(
                        content="content", tool_calls=None
                    ),
                    index=0,
                    finish_reason=CompletionsFinishReason("stop"),
                )
            ],
            created=created,
            model="gpt-4o",
            usage=CompletionsUsage(
                completion_tokens=0, prompt_tokens=0, total_tokens=0
            ),
        ),
        StreamingChatCompletionsUpdate(
            id="id",
            choices=[
                StreamingChatChoiceUpdate(
                    delta=StreamingChatResponseMessageUpdate(
                        content=None,
                        tool_calls=[tool_call_delta],
                    ),
                    index=0,
                    finish_reason=CompletionsFinishReason("stop"),
                )
            ],
            created=created,
            model="gpt-4o",
            usage=usage,
        ),
    ]

    def generator():
        for chunk in chunks:
            call_response_chunk = AzureCallResponseChunk(chunk=chunk)
            if tool_calls := call_response_chunk.chunk.choices[0].delta.tool_calls:
                assert tool_calls[0].function
                tool_call = ChatCompletionsToolCall(
                    id="id",
                    function=FunctionCall(**tool_calls[0].function),
                )
                yield (
                    call_response_chunk,
                    FormatBook.from_tool_call(tool_call),
                )
            else:
                yield call_response_chunk, None

    stream = AzureStream(
        stream=generator(),
        metadata={},
        tool_types=[FormatBook],
        call_response_type=AzureCallResponse,
        model="gpt-4o",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[ChatRequestMessage({"role": "user", "content": "content"})],
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
    assert stream.cost is None

    format_book = FormatBook.from_tool_call(
        ChatCompletionsToolCall(
            id="id",
            function=FunctionCall(
                arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
                name="FormatBook",
            ),
        )
    )
    assert stream.message_param == {
        "role": "assistant",
        "content": "content",
        "tool_calls": [format_book.tool_call],
    }


def test_construct_call_response(mock_datetime_now) -> None:
    """Tests the `AzureStream.construct_call_response` method."""

    class FormatBook(AzureTool):
        """Returns the title and author nicely formatted."""

        title: str
        author: str

        def call(self) -> None:
            """Dummy call."""

    tool_call = StreamingChatResponseToolCallUpdate(
        id="id",
        function=FunctionCall(
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
            name="FormatBook",
        ),
    )
    usage = CompletionsUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2)
    chunks = [
        StreamingChatCompletionsUpdate(
            id="id",
            model="gpt-4o",
            choices=[
                StreamingChatChoiceUpdate(
                    delta=StreamingChatResponseMessageUpdate(
                        content="content", tool_calls=None
                    ),
                    index=0,
                    finish_reason=CompletionsFinishReason("stop"),
                )
            ],
            created=datetime.fromtimestamp(0),
            usage=CompletionsUsage(
                completion_tokens=0, prompt_tokens=0, total_tokens=0
            ),
        ),
        StreamingChatCompletionsUpdate(
            id="id",
            model="gpt-4o",
            choices=[
                StreamingChatChoiceUpdate(
                    delta=StreamingChatResponseMessageUpdate(
                        content=None,
                        tool_calls=[tool_call],
                    ),
                    index=0,
                    finish_reason=CompletionsFinishReason("stop"),
                )
            ],
            created=datetime.fromtimestamp(0),
            usage=usage,
        ),
    ]

    tool_call = None

    def generator():
        nonlocal tool_call
        for chunk in chunks:
            call_response_chunk = AzureCallResponseChunk(chunk=chunk)
            if tool_calls := call_response_chunk.chunk.choices[0].delta.tool_calls:
                assert tool_calls[0].function
                tool_call = ChatCompletionsToolCall(
                    id="id",
                    function=FunctionCall(**tool_calls[0].function),
                )
                yield (
                    call_response_chunk,
                    FormatBook.from_tool_call(tool_call),
                )
            else:
                yield call_response_chunk, None

    stream = AzureStream(
        stream=generator(),
        metadata={},
        tool_types=[FormatBook],
        call_response_type=AzureCallResponse,
        model="gpt-4o",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[UserMessage(content="content")],
        call_params={},
        call_kwargs={},
    )

    for _ in stream:
        pass

    tool_call = ChatCompletionsToolCall(
        function=FunctionCall(
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
            name="FormatBook",
        ),
        id="id",
    )
    completion = ChatCompletions(
        choices=[
            ChatChoice(
                finish_reason="stop",
                index=0,
                message=ChatResponseMessage(
                    role="assistant", content="content", tool_calls=[tool_call]
                ),
            )
        ],
        created=datetime.fromtimestamp(0),
        model="gpt-4o",
        usage=usage,
        id="id",
    )
    call_response = AzureCallResponse(
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
    assert dict(constructed_call_response.response) == dict(call_response.response)


def test_construct_call_response_no_usage() -> None:
    """Tests the `AzureStream.construct_call_response` method with no usage."""
    chunks = [
        StreamingChatCompletionsUpdate(
            id="id",
            choices=[
                StreamingChatChoiceUpdate(
                    delta=StreamingChatResponseMessageUpdate(
                        content="content", tool_calls=None
                    ),
                    index=0,
                    finish_reason=CompletionsFinishReason("stop"),
                )
            ],
            created=datetime.fromtimestamp(0),
            model="gpt-4o",
            usage=CompletionsUsage(
                completion_tokens=0, prompt_tokens=0, total_tokens=0
            ),
        ),
    ]

    def generator():
        for chunk in chunks:
            call_response_chunk = AzureCallResponseChunk(chunk=chunk)
            yield call_response_chunk, None

    stream = AzureStream(
        stream=generator(),
        metadata={},
        tool_types=None,
        call_response_type=AzureCallResponse,
        model="gpt-4o",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[UserMessage(content="content")],
        call_params={},
        call_kwargs={},
    )
    for _ in stream:
        pass
    constructed_call_response = stream.construct_call_response()
    assert constructed_call_response.usage == {
        "completion_tokens": 0,
        "prompt_tokens": 0,
        "total_tokens": 0,
    }
