"""Tests the `openai.stream` module."""

from openai.types.chat import ChatCompletionChunk
from openai.types.chat.chat_completion_chunk import (
    Choice,
    ChoiceDelta,
    ChoiceDeltaToolCall,
    ChoiceDeltaToolCallFunction,
)
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

        def call(self) -> str:
            return f"{self.title} by {self.author}"

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
            model="gpt-4o",
            object="chat.completion.chunk",
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
        "tool_calls": [tool_call],
    }
