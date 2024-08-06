"""Tests the `openai.stream` module."""

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

        def call(self):
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
    assert stream.cost is None
    for _ in stream:
        pass
    assert stream.cost == 2e-5
    assert stream.message_param == {
        "role": "assistant",
        "content": "content",
        "tool_calls": [tool_call.model_dump()],  # type: ignore
    }


def test_construct_call_response():
    class FormatBook(OpenAITool):
        """Returns the title and author nicely formatted."""

        title: str
        author: str

        def call(self):
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
    assert constructed_call_response._provider == call_response._provider
    assert constructed_call_response.content == call_response.content
    assert constructed_call_response.finish_reasons == call_response.finish_reasons
    assert constructed_call_response.model == call_response.model
    assert constructed_call_response.id == call_response.id
    assert constructed_call_response.usage == call_response.usage
    assert constructed_call_response.input_tokens == call_response.input_tokens
    assert constructed_call_response.output_tokens == call_response.output_tokens
    assert constructed_call_response.cost == call_response.cost
    assert constructed_call_response.message_param == call_response.message_param
    assert constructed_call_response.tools == call_response.tools
    assert constructed_call_response.tool == call_response.tool
