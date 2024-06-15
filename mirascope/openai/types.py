"""Types for interacting with OpenAI models using Mirascope."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Generator
from typing import Any, Literal, Optional, Type, Union, overload

from httpx import Timeout
from openai._types import Body, Headers, Query
from openai.types import Embedding
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionAssistantMessageParam,
    ChatCompletionChunk,
    ChatCompletionMessageToolCall,
    ChatCompletionToolChoiceOptionParam,
    ChatCompletionToolMessageParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_chunk import Choice as ChunkChoice
from openai.types.chat.chat_completion_chunk import ChoiceDelta, ChoiceDeltaToolCall
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.chat.chat_completion_message_tool_call import Function
from openai.types.chat.completion_create_params import ResponseFormat
from openai.types.completion_usage import CompletionUsage
from openai.types.create_embedding_response import CreateEmbeddingResponse
from pydantic import ConfigDict

from ..base import (
    BaseAsyncStream,
    BaseCallParams,
    BaseCallResponse,
    BaseCallResponseChunk,
    BaseStream,
    BaseToolStream,
)
from ..partial import partial
from ..rag import BaseEmbeddingParams, BaseEmbeddingResponse
from .tools import OpenAITool


class OpenAICallParams(BaseCallParams[OpenAITool]):
    """The parameters to use when calling the OpenAI API."""

    model: str = "gpt-4o-2024-05-13"
    frequency_penalty: Optional[float] = None
    logit_bias: Optional[dict[str, int]] = None
    logprobs: Optional[bool] = None
    max_tokens: Optional[int] = None
    n: Optional[int] = None
    presence_penalty: Optional[float] = None
    response_format: Optional[ResponseFormat] = None
    seed: Optional[int] = None
    stop: Union[Optional[str], list[str]] = None
    temperature: Optional[float] = None
    tool_choice: Optional[ChatCompletionToolChoiceOptionParam] = None
    top_logprobs: Optional[int] = None
    top_p: Optional[float] = None
    user: Optional[str] = None
    # Values defined below take precedence over values defined elsewhere. Use these
    # params to pass additional parameters to the API if necessary that aren't already
    # available as params.
    extra_headers: Optional[Headers] = None
    extra_query: Optional[Query] = None
    extra_body: Optional[Body] = None
    timeout: Optional[Union[float, Timeout]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def kwargs(
        self,
        tool_type: Optional[Type[OpenAITool]] = OpenAITool,
        exclude: Optional[set[str]] = None,
    ) -> dict[str, Any]:
        """Returns the keyword argument call parameters."""
        return super().kwargs(tool_type, exclude)


class OpenAICallResponse(BaseCallResponse[ChatCompletion, OpenAITool]):
    """A convenience wrapper around the OpenAI `ChatCompletion` response.

    When using Mirascope's convenience wrappers to interact with OpenAI models via
    `OpenAICall`, responses using `OpenAICall.call()` will return a
    `OpenAICallResponse`, whereby the implemented properties allow for simpler syntax
    and a convenient developer experience.

    Example:

    ```python
    from mirascope.openai import OpenAICall


    class BookRecommender(OpenAICall):
        prompt_template = "Please recommend a {genre} book"

        genre: str


    response = Bookrecommender(genre="fantasy").call()
    print(response.content)
    #> The Name of the Wind

    print(response.message)
    #> ChatCompletionMessage(content='The Name of the Wind', role='assistant',
    #  function_call=None, tool_calls=None)

    print(response.choices)
    #> [Choice(finish_reason='stop', index=0, logprobs=None,
    #  message=ChatCompletionMessage(content='The Name of the Wind', role='assistant',
    #  function_call=None, tool_calls=None))]
    ```
    """

    response_format: Optional[ResponseFormat] = None
    user_message_param: Optional[ChatCompletionUserMessageParam] = None

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
    def tool_calls(self) -> Optional[list[ChatCompletionMessageToolCall]]:
        """Returns the tool calls for the 0th choice message."""
        return self.message.tool_calls

    @property
    def tools(self) -> Optional[list[OpenAITool]]:
        """Returns the tools for the 0th choice message.

        Raises:
            ValidationError: if a tool call doesn't match the tool's schema.
        """
        if not self.tool_types:
            return None

        if self.choice.finish_reason == "length":
            raise RuntimeError(
                "Finish reason was `length`, indicating the model ran out of tokens "
                "(and could not complete the tool call if trying to)"
            )

        def reconstruct_tools_from_content() -> list[OpenAITool]:
            # Note: we only handle single tool calls in this case
            tool_type = self.tool_types[0]  # type: ignore
            return [
                tool_type.from_tool_call(
                    ChatCompletionMessageToolCall(
                        id="id",
                        function=Function(
                            name=tool_type.name(), arguments=self.content
                        ),
                        type="function",
                    )
                )
            ]

        if self.response_format == ResponseFormat(type="json_object"):
            return reconstruct_tools_from_content()

        if not self.tool_calls:
            # Let's see if we got an assistant message back instead and try to
            # reconstruct a tool call in this case. We'll assume if it starts with
            # an open curly bracket that we got a tool call assistant message.
            if "{" == self.content[0]:
                # Note: we only handle single tool calls in JSON mode.
                return reconstruct_tools_from_content()
            return None

        extracted_tools = []
        for tool_call in self.tool_calls:
            for tool_type in self.tool_types:
                if tool_call.function.name == tool_type.name():
                    extracted_tools.append(tool_type.from_tool_call(tool_call))
                    break

        return extracted_tools

    @property
    def tool(self) -> Optional[OpenAITool]:
        """Returns the 0th tool for the 0th choice message.

        Raises:
            ValidationError: if the tool call doesn't match the tool's schema.
        """
        tools = self.tools
        if tools:
            return tools[0]
        return None

    @classmethod
    def tool_message_params(
        self, tools_and_outputs: list[tuple[OpenAITool, str]]
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
    def usage(self) -> Optional[CompletionUsage]:
        """Returns the usage of the chat completion."""
        if self.response.usage:
            return self.response.usage
        return None

    @property
    def input_tokens(self) -> Optional[int]:
        """Returns the number of input tokens."""
        if self.usage:
            return self.usage.prompt_tokens
        return None

    @property
    def output_tokens(self) -> Optional[int]:
        """Returns the number of output tokens."""
        if self.usage:
            return self.usage.completion_tokens
        return None

    def dump(self) -> dict[str, Any]:
        """Dumps the response to a dictionary."""
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "output": self.response.model_dump(),
            "cost": self.cost,
        }


class OpenAICallResponseChunk(BaseCallResponseChunk[ChatCompletionChunk, OpenAITool]):
    """Convenience wrapper around chat completion streaming chunks.

    When using Mirascope's convenience wrappers to interact with OpenAI models via
    `OpenAICall.stream`, responses will return an `OpenAICallResponseChunk`, whereby
    the implemented properties allow for simpler syntax and a convenient developer
    experience.

    Example:

    ```python
    from mirascope.openai import OpenAICall


    class Math(OpenAICall):
        prompt_template = "What is 1 + 2?"


    content = ""
    for chunk in Math().stream():
        content += chunk.content
        print(content)
    #> 1
    #  1 +
    #  1 + 2
    #  1 + 2 equals
    #  1 + 2 equals
    #  1 + 2 equals 3
    #  1 + 2 equals 3.
    ```
    """

    response_format: Optional[ResponseFormat] = None
    user_message_param: Optional[ChatCompletionUserMessageParam] = None

    @property
    def choices(self) -> list[ChunkChoice]:
        """Returns the array of chat completion choices."""
        return self.chunk.choices

    @property
    def choice(self) -> ChunkChoice:
        """Returns the 0th choice."""
        return self.chunk.choices[0]

    @property
    def delta(self) -> Optional[ChoiceDelta]:
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
    def tool_calls(self) -> Optional[list[ChoiceDeltaToolCall]]:
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
    def usage(self) -> Optional[CompletionUsage]:
        """Returns the usage of the chat completion."""
        if self.chunk.usage:
            return self.chunk.usage
        return None

    @property
    def input_tokens(self) -> Optional[int]:
        """Returns the number of input tokens."""
        if self.usage:
            return self.usage.prompt_tokens
        return None

    @property
    def output_tokens(self) -> Optional[int]:
        """Returns the number of output tokens."""
        if self.usage:
            return self.usage.completion_tokens
        return None


class OpenAIEmbeddingResponse(BaseEmbeddingResponse[CreateEmbeddingResponse]):
    """A convenience wrapper around the OpenAI `CreateEmbeddingResponse` response."""

    @property
    def embeddings(self) -> list[list[float]]:
        """Returns the raw embeddings."""
        embeddings_model: list[Embedding] = [
            embedding for embedding in self.response.data
        ]
        return [embedding.embedding for embedding in embeddings_model]


class OpenAIEmbeddingParams(BaseEmbeddingParams):
    model: str = "text-embedding-3-small"
    encoding_format: Optional[Literal["float", "base64"]] = None
    user: Optional[str] = None
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Optional[Headers] = None
    extra_query: Optional[Query] = None
    extra_body: Optional[Body] = None
    timeout: Optional[Union[float, Timeout]] = None


def _handle_chunk(
    chunk: OpenAICallResponseChunk,
    current_tool_call: ChatCompletionMessageToolCall,
    current_tool_type: Optional[Type[OpenAITool]],
    allow_partial: bool,
) -> tuple[
    Optional[OpenAITool],
    ChatCompletionMessageToolCall,
    Optional[Type[OpenAITool]],
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


class OpenAIToolStream(BaseToolStream[OpenAICallResponseChunk, OpenAITool]):
    """A base class for streaming tools from response chunks."""

    @classmethod
    @overload
    def from_stream(
        cls,
        stream: Generator[OpenAICallResponseChunk, None, None],
        allow_partial: Literal[True],
    ) -> Generator[Optional[OpenAITool], None, None]:
        yield ...  # type: ignore  # pragma: no cover

    @classmethod
    @overload
    def from_stream(
        cls,
        stream: Generator[OpenAICallResponseChunk, None, None],
        allow_partial: Literal[False],
    ) -> Generator[OpenAITool, None, None]:
        yield ...  # type: ignore  # pragma: no cover

    @classmethod
    @overload
    def from_stream(
        cls,
        stream: Generator[OpenAICallResponseChunk, None, None],
        allow_partial: bool = False,
    ) -> Generator[Optional[OpenAITool], None, None]:
        yield ...  # type: ignore  # pragma: no cover

    @classmethod
    def from_stream(cls, stream, allow_partial=False):
        """Yields partial tools from the given stream of chunks.

        Args:
            stream: The generator of chunks from which to stream tools.
            allow_partial: Whether to allow partial tools.

        Raises:
            RuntimeError: if a tool in the stream is of an unknown type.
        """
        cls._check_version_for_partial(allow_partial)
        current_tool_call = ChatCompletionMessageToolCall(
            id="", function=Function(arguments="", name=""), type="function"
        )
        current_tool_type = None
        for chunk in stream:
            tool, current_tool_call, current_tool_type, starting_new = _handle_chunk(
                chunk, current_tool_call, current_tool_type, allow_partial
            )
            if tool is not None:
                yield tool
            if starting_new and allow_partial:
                yield None
        if current_tool_type:
            yield current_tool_type.from_tool_call(current_tool_call)

    @classmethod
    @overload
    async def from_async_stream(
        cls,
        stream: AsyncGenerator[OpenAICallResponseChunk, None],
        allow_partial: Literal[True],
    ) -> AsyncGenerator[Optional[OpenAITool], None]:
        yield ...  # type: ignore  # pragma: no cover

    @classmethod
    @overload
    async def from_async_stream(
        cls,
        stream: AsyncGenerator[OpenAICallResponseChunk, None],
        allow_partial: Literal[False],
    ) -> AsyncGenerator[OpenAITool, None]:
        yield ...  # type: ignore  # pragma: no cover

    @classmethod
    @overload
    async def from_async_stream(
        cls,
        stream: AsyncGenerator[OpenAICallResponseChunk, None],
        allow_partial: bool = False,
    ) -> AsyncGenerator[Optional[OpenAITool], None]:
        yield ...  # type: ignore  # pragma: no cover

    @classmethod
    async def from_async_stream(cls, async_stream, allow_partial=False):
        """Yields partial tools from the given stream of chunks asynchronously.

        Args:
            stream: The async generator of chunks from which to stream tools.
            allow_partial: Whether to allow partial tools.

        Raises:
            RuntimeError: if a tool in the stream is of an unknown type.
        """
        cls._check_version_for_partial(allow_partial)
        current_tool_call = ChatCompletionMessageToolCall(
            id="", function=Function(arguments="", name=""), type="function"
        )
        current_tool_type = None
        async for chunk in async_stream:
            tool, current_tool_call, current_tool_type, starting_new = _handle_chunk(
                chunk, current_tool_call, current_tool_type, allow_partial
            )
            if tool is not None:
                yield tool
            if starting_new and allow_partial:
                yield None
        if current_tool_type:
            yield current_tool_type.from_tool_call(current_tool_call)


class OpenAIStream(
    BaseStream[
        OpenAICallResponseChunk,
        ChatCompletionUserMessageParam,
        ChatCompletionAssistantMessageParam,
        OpenAITool,
    ]
):
    """A class for streaming responses from OpenAI's API."""

    def __init__(
        self,
        stream: Generator[OpenAICallResponseChunk, None, None],
        allow_partial: bool = False,
    ):
        """Initializes an instance of `OpenAIStream`."""
        OpenAIToolStream._check_version_for_partial(allow_partial)
        super().__init__(stream, ChatCompletionAssistantMessageParam)
        self._allow_partial = allow_partial

    def __iter__(
        self,
    ) -> Generator[tuple[OpenAICallResponseChunk, Optional[OpenAITool]], None, None]:
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
            tool, current_tool_call, current_tool_type, starting_new = _handle_chunk(
                chunk, current_tool_call, current_tool_type, self._allow_partial
            )
            if tool is not None:
                yield chunk, tool
                if starting_new:
                    tool_calls.append(tool.tool_call)
            if starting_new and self._allow_partial:
                yield chunk, None
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

    def __init__(
        self,
        stream: AsyncGenerator[OpenAICallResponseChunk, None],
        allow_partial: bool = False,
    ):
        """Initializes an instance of `OpenAIAsyncStream`."""
        OpenAIToolStream._check_version_for_partial(allow_partial)
        super().__init__(stream, ChatCompletionAssistantMessageParam)
        self._allow_partial = allow_partial

    def __aiter__(
        self,
    ) -> AsyncGenerator[tuple[OpenAICallResponseChunk, Optional[OpenAITool]], None]:
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
                    starting_new,
                ) = _handle_chunk(
                    chunk, current_tool_call, current_tool_type, self._allow_partial
                )
                if tool is not None:
                    yield chunk, tool
                    if starting_new:
                        tool_calls.append(tool.tool_call)
                if starting_new and self._allow_partial:
                    yield chunk, None
            if tool_calls:
                self.message_param["tool_calls"] = tool_calls  # type: ignore

        return generator()

    @classmethod
    def tool_message_params(cls, tools_and_outputs):
        """Returns the tool message parameters for tool call results."""
        return OpenAICallResponse.tool_message_params(tools_and_outputs)
