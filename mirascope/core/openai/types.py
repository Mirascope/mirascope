"""Types for the Mirascope OpenAI module."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Generator

import jiter
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionAssistantMessageParam,
    ChatCompletionChunk,
    ChatCompletionMessage,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCall,
    ChatCompletionStreamOptionsParam,
    ChatCompletionToolChoiceOptionParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_chunk import Choice as ChunkChoice
from openai.types.chat.chat_completion_chunk import ChoiceDelta, ChoiceDeltaToolCall
from openai.types.chat.chat_completion_message_tool_call import Function
from openai.types.chat.completion_create_params import ResponseFormat
from openai.types.completion_usage import CompletionUsage
from openai.types.shared_params import FunctionDefinition
from pydantic import computed_field
from typing_extensions import NotRequired, Required

from .._internal.partial import partial
from ..base.types import (
    BaseAsyncStream,
    BaseCallParams,
    BaseCallResponse,
    BaseCallResponseChunk,
    BaseFunctionReturn,
    BaseStream,
    BaseTool,
)


class OpenAITool(BaseTool):
    """A class for defining tools for OpenAI LLM calls."""

    tool_call: ChatCompletionMessageToolCall

    @classmethod
    def tool_schema(cls) -> ChatCompletionToolParam:
        """Constructs a JSON Schema tool schema from the `BaseModel` schema defined."""
        model_schema = cls.model_json_schema()
        model_schema.pop("title", None)
        model_schema.pop("description", None)

        fn = FunctionDefinition(name=cls.name(), description=cls.description())
        if model_schema["properties"]:
            fn["parameters"] = model_schema

        return ChatCompletionToolParam(function=fn, type="function")

    @classmethod
    def from_tool_call(
        cls, tool_call: ChatCompletionMessageToolCall, allow_partial: bool = False
    ) -> OpenAITool:
        """Constructs an `OpenAITool` instance from a `tool_call`."""
        model_json = jiter.from_json(
            tool_call.function.arguments.encode(),
            partial_mode="trailing-strings" if allow_partial else "off",
        )
        model_json["tool_call"] = tool_call.model_dump()
        return cls.model_validate(model_json)


class OpenAICallParams(BaseCallParams):
    """The parameters to use when calling the OpenAI API."""

    model: Required[str]
    frequency_penalty: NotRequired[float | None]
    logit_bias: NotRequired[dict[str, int] | None]
    logprobs: NotRequired[bool | None]
    max_tokens: NotRequired[int | None]
    n: NotRequired[int | None]
    parallel_tool_calls: NotRequired[bool]
    presence_penalty: NotRequired[float | None]
    response_format: NotRequired[ResponseFormat]
    seed: NotRequired[int | None]
    stop: NotRequired[str | list[str] | None]
    stream_options: NotRequired[ChatCompletionStreamOptionsParam | None]
    temperature: NotRequired[float | None]
    tool_choice: NotRequired[ChatCompletionToolChoiceOptionParam]
    top_logprobs: NotRequired[int | None]
    top_p: NotRequired[float | None]
    user: NotRequired[str]


OpenAICallFunctionReturn = BaseFunctionReturn[
    ChatCompletionMessageParam, OpenAICallParams
]
'''The function return type for functions wrapped with the `openai_call` decorator.

Attributes:
    computed_fields: The computed fields to use in the prompt template.
    messages: The messages to send to the OpenAI API. If provided, `computed_fields`
        will be ignored.
    call_params: The call parameters to use when calling the OpenAI API. These will
        override any call parameters provided to the decorator.

Example:

```python
from mirascope.core.openai import OpenAICallFunctionReturn, openai_call

@openai_call(model="gpt-4o")
def recommend_book(genre: str) -> OpenAICallFunctionReturn:
    """Recommend a {capitalized_genre} book."""
    reeturn {"computed_fields": {"capitalized_genre": genre.capitalize()}}
```
'''


class OpenAICallResponse(
    BaseCallResponse[
        ChatCompletion,
        OpenAITool,
        OpenAICallFunctionReturn,
        ChatCompletionMessageParam,
        OpenAICallParams,
        ChatCompletionUserMessageParam,
    ]
):
    '''A convenience wrapper around the OpenAI `ChatCompletion` response.

    When calling the OpenAI API using a function decorated with `openai_call`, the
    response will be an `OpenAICallResponse` instance with properties that allow for
    more convenience access to commonly used attributes.

    Example:

    ```python
    from mirascope.core.openai import openai_call

    @openai_call(model="gpt-4o")
    def recommend_book(genre: str):
        """Recommend a {genre} book."""

    response = recommend_book("fantasy")  # response is an `OpenAICallResponse` instance
    print(response.content)
    #> Sure! I would recommend...
    ```
    '''

    @computed_field
    @property
    def message_param(self) -> ChatCompletionAssistantMessageParam:
        """Returns the assistants's response as a message parameter."""
        return self.message.model_dump(exclude={"function_call"})  # type: ignore

    @property
    def choices(self) -> list[Choice]:
        """Returns the array of chat completion choices."""
        return self.response.choices

    @property
    def choice(self) -> Choice:
        """Returns the 0th choice."""
        return self.choices[0]

    @property
    def message(self) -> ChatCompletionMessage:
        """Returns the message of the chat completion for the 0th choice."""
        return self.choice.message

    @property
    def content(self) -> str:
        """Returns the content of the chat completion for the 0th choice."""
        return self.message.content if self.message.content is not None else ""

    @property
    def model(self) -> str:
        """Returns the name of the response model."""
        return self.response.model

    @property
    def id(self) -> str:
        """Returns the id of the response."""
        return self.response.id

    @property
    def finish_reasons(self) -> list[str]:
        """Returns the finish reasons of the response."""
        return [str(choice.finish_reason) for choice in self.response.choices]

    @property
    def tool_calls(self) -> list[ChatCompletionMessageToolCall] | None:
        """Returns the tool calls for the 0th choice message."""
        return self.message.tool_calls

    @computed_field
    @property
    def tools(self) -> list[OpenAITool] | None:
        """Returns any available tool calls as their `OpenAITool` definition.

        Raises:
            ValidationError: if a tool call doesn't match the tool's schema.
        """
        if not self.tool_types or not self.tool_calls:
            return None

        extracted_tools = []
        for tool_call in self.tool_calls:
            for tool_type in self.tool_types:
                if tool_call.function.name == tool_type.name():
                    extracted_tools.append(tool_type.from_tool_call(tool_call))
                    break

        return extracted_tools

    @computed_field
    @property
    def tool(self) -> OpenAITool | None:
        """Returns the 0th tool for the 0th choice message.

        Raises:
            ValidationError: if the tool call doesn't match the tool's schema.
        """
        if tools := self.tools:
            return tools[0]
        return None

    @classmethod
    def tool_message_params(
        cls, tools_and_outputs: list[tuple[OpenAITool, str]]
    ) -> list[ChatCompletionToolMessageParam]:
        return [
            ChatCompletionToolMessageParam(
                role="tool",
                content=output,
                tool_call_id=tool.tool_call.id,
                name=tool.name(),  # type: ignore
            )
            for tool, output in tools_and_outputs
        ]

    @property
    def usage(self) -> CompletionUsage | None:
        """Returns the usage of the chat completion."""
        return self.response.usage

    @property
    def input_tokens(self) -> int | None:
        """Returns the number of input tokens."""
        return self.usage.prompt_tokens if self.usage else None

    @property
    def output_tokens(self) -> int | None:
        """Returns the number of output tokens."""
        return self.usage.completion_tokens if self.usage else None


class OpenAICallResponseChunk(
    BaseCallResponseChunk[
        ChatCompletionChunk, OpenAITool, ChatCompletionUserMessageParam
    ]
):
    '''A convenience wrapper around the OpenAI `ChatCompletionChunk` streamed chunks.

    When calling the OpenAI API using a function decorated with `openai_call` and
    `stream` set to `True`, the stream will contain `OpenAIResponseChunk` instances with
    properties that allow for more convenient access to commonly used attributes.

    Example:

    ```python
    from mirascope.core.openai import openai_call

    @openai_call(model="gpt-4o", stream=True)
    def recommend_book(genre: str):
        """Recommend a {genre} book."""

    stream = recommend_book("fantasy")  # response is an `OpenAIStream`
    for chunk in stream:
        print(chunk.content, end="", flush=True)
    #> Sure! I would recommend...
    ```
    '''

    @property
    def choices(self) -> list[ChunkChoice]:
        """Returns the array of chat completion choices."""
        return self.chunk.choices

    @property
    def choice(self) -> ChunkChoice:
        """Returns the 0th choice."""
        return self.chunk.choices[0]

    @property
    def delta(self) -> ChoiceDelta | None:
        """Returns the delta for the 0th choice."""
        if self.chunk.choices:
            return self.chunk.choices[0].delta
        return None

    @property
    def content(self) -> str:
        """Returns the content for the 0th choice delta."""
        return (
            self.delta.content if self.delta is not None and self.delta.content else ""
        )

    @property
    def model(self) -> str:
        """Returns the name of the response model."""
        return self.chunk.model

    @property
    def id(self) -> str:
        """Returns the id of the response."""
        return self.chunk.id

    @property
    def finish_reasons(self) -> list[str]:
        """Returns the finish reasons of the response."""
        return [str(choice.finish_reason) for choice in self.chunk.choices]

    @property
    def tool_calls(self) -> list[ChoiceDeltaToolCall] | None:
        """Returns the partial tool calls for the 0th choice message.

        The first `list[ChoiceDeltaToolCall]` will contain the name of the tool and
        index, and subsequent `list[ChoiceDeltaToolCall]`s will contain the arguments
        which will be strings that need to be concatenated with future
        `list[ChoiceDeltaToolCall]`s to form a complete JSON tool calls. The last
        `list[ChoiceDeltaToolCall]` will be None indicating end of stream.
        """
        if self.delta:
            return self.delta.tool_calls
        return None

    @property
    def usage(self) -> CompletionUsage | None:
        """Returns the usage of the chat completion."""
        if self.chunk.usage:
            return self.chunk.usage
        return None

    @property
    def input_tokens(self) -> int | None:
        """Returns the number of input tokens."""
        if self.usage:
            return self.usage.prompt_tokens
        return None

    @property
    def output_tokens(self) -> int | None:
        """Returns the number of output tokens."""
        if self.usage:
            return self.usage.completion_tokens
        return None


def _handle_chunk(
    chunk: OpenAICallResponseChunk,
    current_tool_call: ChatCompletionMessageToolCall,
    current_tool_type: type[OpenAITool] | None,
    allow_partial: bool,
) -> tuple[
    OpenAITool | None,
    ChatCompletionMessageToolCall,
    type[OpenAITool] | None,
    bool,
]:
    """Handles a chunk of the stream."""
    if not chunk.tool_types or not chunk.tool_calls:
        return None, current_tool_call, current_tool_type, False

    tool_call = chunk.tool_calls[0]
    # Reset on new tool
    if tool_call.id and tool_call.function is not None:
        previous_tool_call = current_tool_call.model_copy()
        previous_tool_type = current_tool_type
        current_tool_call = ChatCompletionMessageToolCall(
            id=tool_call.id,
            function=Function(
                arguments="",
                name=tool_call.function.name if tool_call.function.name else "",
            ),
            type="function",
        )
        current_tool_type = None
        for tool_type in chunk.tool_types:
            if tool_type.name() == tool_call.function.name:
                current_tool_type = tool_type
                break
        if current_tool_type is None:
            raise RuntimeError(
                f"Unknown tool type in stream: {tool_call.function.name}"
            )
        if previous_tool_call.id and previous_tool_type is not None:
            return (
                previous_tool_type.from_tool_call(
                    previous_tool_call, allow_partial=allow_partial
                ),
                current_tool_call,
                current_tool_type,
                True,
            )

    # Update arguments with each chunk
    if tool_call.function and tool_call.function.arguments:
        current_tool_call.function.arguments += tool_call.function.arguments

        if allow_partial and current_tool_type:
            return (
                partial(current_tool_type).from_tool_call(
                    current_tool_call, allow_partial=True
                ),
                current_tool_call,
                current_tool_type,
                False,
            )

    return None, current_tool_call, current_tool_type, False


class OpenAIStream(
    BaseStream[
        OpenAICallResponseChunk,
        ChatCompletionUserMessageParam,
        ChatCompletionAssistantMessageParam,
        OpenAITool,
    ]
):
    """A class for streaming responses from OpenAI's API."""

    def __init__(self, stream: Generator[OpenAICallResponseChunk, None, None]):
        """Initializes an instance of `OpenAIStream`."""
        super().__init__(stream, ChatCompletionAssistantMessageParam)

    def __iter__(
        self,
    ) -> Generator[tuple[OpenAICallResponseChunk, OpenAITool | None], None, None]:
        """Iterator over the stream and constructs tools as they are streamed."""
        current_tool_call = ChatCompletionMessageToolCall(
            id="", function=Function(arguments="", name=""), type="function"
        )
        current_tool_type, tool_calls = None, []
        for chunk, _ in super().__iter__():
            if not chunk.tool_types or not chunk.tool_calls:
                if current_tool_type:
                    yield chunk, current_tool_type.from_tool_call(current_tool_call)
                    tool_calls.append(current_tool_call)
                    current_tool_type = None
                else:
                    yield chunk, None
            tool, current_tool_call, current_tool_type, _ = _handle_chunk(
                chunk, current_tool_call, current_tool_type, False
            )
            if tool is not None:
                yield chunk, tool
                tool_calls.append(tool.tool_call)
        if tool_calls:
            self.message_param["tool_calls"] = tool_calls  # type: ignore

    @classmethod
    def tool_message_params(cls, tools_and_outputs):
        """Returns the tool message parameters for tool call results."""
        return OpenAICallResponse.tool_message_params(tools_and_outputs)


class OpenAIAsyncStream(
    BaseAsyncStream[
        OpenAICallResponseChunk,
        ChatCompletionUserMessageParam,
        ChatCompletionAssistantMessageParam,
        OpenAITool,
    ]
):
    """A class for streaming responses from OpenAI's API."""

    def __init__(self, stream: AsyncGenerator[OpenAICallResponseChunk, None]):
        """Initializes an instance of `OpenAIAsyncStream`."""
        super().__init__(stream, ChatCompletionAssistantMessageParam)

    def __aiter__(
        self,
    ) -> AsyncGenerator[tuple[OpenAICallResponseChunk, OpenAITool | None], None]:
        """Iterator over the stream and constructs tools as they are streamed."""
        stream = super().__aiter__()

        async def generator():
            current_tool_call = ChatCompletionMessageToolCall(
                id="", function=Function(arguments="", name=""), type="function"
            )
            current_tool_type, tool_calls = None, []
            async for chunk, _ in stream:
                if not chunk.tool_types or not chunk.tool_calls:
                    if current_tool_type:
                        yield chunk, current_tool_type.from_tool_call(current_tool_call)
                        tool_calls.append(current_tool_call)
                        current_tool_type = None
                    else:
                        yield chunk, None
                (
                    tool,
                    current_tool_call,
                    current_tool_type,
                    _,
                ) = _handle_chunk(chunk, current_tool_call, current_tool_type, False)
                if tool is not None:
                    yield chunk, tool
                    tool_calls.append(tool.tool_call)
            if tool_calls:
                self.message_param["tool_calls"] = tool_calls  # type: ignore

        return generator()

    @classmethod
    def tool_message_params(cls, tools_and_outputs):
        """Returns the tool message parameters for tool call results."""
        return OpenAICallResponse.tool_message_params(tools_and_outputs)
