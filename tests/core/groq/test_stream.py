"""Tests the `groq.stream` module."""

from groq.types.chat import ChatCompletionChunk
from groq.types.chat.chat_completion_chunk import (
    Choice,
    ChoiceDelta,
    ChoiceDeltaToolCall,
    ChoiceDeltaToolCallFunction,
)
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
                Choice(delta=ChoiceDelta(content="content", tool_calls=None), index=0)
            ],
            created=0,
            model="llama3-70b-8192",
            object="chat.completion.chunk",
            x_groq=None,
        ),
        ChatCompletionChunk(
            id="id",
            choices=[
                Choice(
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
    assert stream.cost is None
    for _ in stream:
        pass
    assert stream.cost == 1.38e-6
    assert stream.message_param == {
        "role": "assistant",
        "content": "content",
        "tool_calls": [tool_call],
    }
