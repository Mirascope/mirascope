"""Types for interacting with Groq's Cloud API using Mirascope."""

from collections.abc import AsyncGenerator, Generator
from typing import Any, Optional, Type, Union

from groq._types import Body, Headers, Query
from groq.types.chat import (
    ChatCompletion,
    ChatCompletionAssistantMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionUserMessageParam,
)
from groq.types.chat.chat_completion import (
    ChatCompletionMessage,
    Choice,
    CompletionUsage,
)
from groq.types.chat.chat_completion_chunk import (
    ChatCompletionChunk,
    ChoiceDelta,
    ChoiceDeltaToolCall,
)
from groq.types.chat.chat_completion_chunk import Choice as ChunkChoice
from groq.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from groq.types.chat.completion_create_params import (
    ChatCompletionToolChoiceOptionParam,
    ResponseFormat,
)
from httpx import Timeout
from pydantic import ConfigDict

from ..base import (
    BaseAsyncStream,
    BaseCallParams,
    BaseCallResponse,
    BaseCallResponseChunk,
    BaseStream,
)
from .tools import GroqTool


class GroqCallParams(BaseCallParams[GroqTool]):
    """The parameters to use when calling the Groq Cloud API."""

    model: str = "mixtral-8x7b-32768"
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
        tool_type: Optional[Type[GroqTool]] = GroqTool,
        exclude: Optional[set[str]] = None,
    ) -> dict[str, Any]:
        """Returns the keyword argument call parameters."""
        return super().kwargs(tool_type, exclude)


class GroqCallResponse(BaseCallResponse[ChatCompletion, GroqTool]):
    """A convenience wrapper around the Groq `ChatCompletion` response.

    When using Mirascope's convenience wrappers to interact with Groq models via
    `GroqCall`, responses using `GroqCall.call()` will return a
    `GroqCallResponse`, whereby the implemented properties allow for simpler syntax
    and a convenient developer experience.

    Example:

    ```python
    from mirascope.groq import GroqCall


    class BookRecommender(GroqCall):
        prompt_template = "Please recommend a {genre} book"

        genre: str


    response = Bookrecommender(genre="fantasy").call()
    print(response.content)
    #> The Name of the Wind

    print(response.message)
    #> ChatCompletion(content='The Name of the Wind', role='assistant',
    #  function_call=None, tool_calls=None)

    print(response.choices)
    #> [Choice(finish_reason='stop', index=0, logprobs=None,
    #  message=ChatCompletion(content='The Name of the Wind', role='assistant',
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
    def tool_calls(self) -> Optional[list[ChatCompletionMessageToolCall]]:
        """Returns the tool calls for the 0th choice message."""
        return self.message.tool_calls

    @property
    def tools(self) -> Optional[list[GroqTool]]:
        """Returns the tools for the 0th choice message.

        Raises:
            ValidationError: if a tool call doesn't match the tool's schema.
        """
        if not self.tool_types:
            return None

        if self.choice.finish_reason == "length":
            raise RuntimeError(
                "Finish reason was `length`, indicating the model ran out of tokens "
                "(and likely could not complete the tool call if trying to)"
            )

        def reconstruct_tools_from_content() -> list[GroqTool]:
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
                if tool_call.function and tool_call.function.name == tool_type.name():
                    extracted_tools.append(tool_type.from_tool_call(tool_call))
                    break

        return extracted_tools

    @property
    def tool(self) -> Optional[GroqTool]:
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
        self, tools_and_outputs: list[tuple[GroqTool, str]]
    ) -> list[ChatCompletionToolMessageParam]:
        """Returns the tool message parameters for tool call results."""
        return [
            {"role": "tool", "content": output, "tool_call_id": tool.tool_call.id}
            for tool, output in tools_and_outputs
        ]

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
        return [str(choice.finish_reason) for choice in self.choices]

    @property
    def usage(self) -> Optional[CompletionUsage]:
        """Returns the usage of the chat completion."""
        return self.response.usage

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


class GroqCallResponseChunk(BaseCallResponseChunk[ChatCompletionChunk, GroqTool]):
    """Convenience wrapper around chat completion streaming chunks.

    When using Mirascope's convenience wrappers to interact with Groq models via
    `Groq.stream`, responses will return an `GroqCallResponseChunk`, whereby
    the implemented properties allow for simpler syntax and a convenient developer
    experience.

    Example:

    ```python
    from mirascope.groq import GroqCall


    class Math(GroqCall):
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
        return self.choices[0]

    @property
    def delta(self) -> ChoiceDelta:
        """Returns the delta for the 0th choice."""
        return self.choice.delta

    @property
    def content(self) -> str:
        """Returns the content for the 0th choice delta."""
        return self.delta.content if self.delta.content is not None else ""

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
        return self.delta.tool_calls

    @property
    def usage(self) -> Optional[CompletionUsage]:
        """Returns the usage of the chat completion."""
        return self.chunk.usage

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


class GroqStream(
    BaseStream[
        GroqCallResponseChunk,
        ChatCompletionUserMessageParam,
        ChatCompletionAssistantMessageParam,
        GroqTool,
    ]
):
    """A class for streaming responses from Groq's API."""

    def __init__(self, stream: Generator[GroqCallResponseChunk, None, None]):
        """Initializes an instance of `GroqStream`."""
        super().__init__(stream, ChatCompletionAssistantMessageParam)


class GroqAsyncStream(
    BaseAsyncStream[
        GroqCallResponseChunk,
        ChatCompletionUserMessageParam,
        ChatCompletionAssistantMessageParam,
        GroqTool,
    ]
):
    """A class for streaming responses from Groq's API."""

    def __init__(self, stream: AsyncGenerator[GroqCallResponseChunk, None]):
        """Initializes an instance of `GroqAsyncStream`."""
        super().__init__(stream, ChatCompletionAssistantMessageParam)
