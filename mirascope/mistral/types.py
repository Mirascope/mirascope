"""Types for working with Mistral prompts."""

from collections.abc import AsyncGenerator, Generator
from typing import Any, Optional

from mistralai.models.chat_completion import (
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatCompletionResponseStreamChoice,
    ChatCompletionStreamResponse,
    ChatMessage,
    DeltaMessage,
    ToolCall,
    ToolChoice,
    UsageInfo,
)
from pydantic import ConfigDict

from ..base import (
    BaseAsyncStream,
    BaseCallParams,
    BaseCallResponse,
    BaseCallResponseChunk,
    BaseStream,
    Message,
    ToolMessage,
)
from ..base.types import AssistantMessage, UserMessage
from .tools import MistralTool


class MistralCallParams(BaseCallParams[MistralTool]):
    """The parameters to use when calling the Mistral API."""

    model: str = "open-mixtral-8x7b"
    endpoint: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    random_seed: Optional[int] = None
    safe_mode: Optional[bool] = None
    safe_prompt: Optional[bool] = None
    tool_choice: Optional[ToolChoice] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)


class MistralCallResponse(BaseCallResponse[ChatCompletionResponse, MistralTool]):
    """Convenience wrapper for Mistral's chat model completions.

    When using Mirascope's convenience wrappers to interact with Mistral models via
    `MistralCall`, responses using `MistralCall.call()` will return a
    `MistralCallResponse`, whereby the implemented properties allow for simpler syntax
    and a convenient developer experience.

    Example:

    ```python
    from mirascope.mistral import MistralCall

    class BookRecommender(MistralCall):
        prompt_template = "Please recommend a {genre} book"

        genre: str

    response = Bookrecommender(genre="fantasy").call()
    print(response.content)
    #> The Name of the Wind

    print(response.message)
    #> ChatMessage(content='The Name of the Wind', role='assistant',
    #  function_call=None, tool_calls=None)

    print(response.choices)
    #> [Choice(finish_reason='stop', index=0, logprobs=None,
    #  message=ChatMessage(content='The Name of the Wind', role='assistant',
    #  function_call=None, tool_calls=None))]
    ```

    """

    user_message_param: Optional[Message] = None

    @property
    def message_param(self) -> Message:
        """Returns the assistants's response as a message parameter."""
        return self.message.model_dump()  # type: ignore

    @property
    def choices(self) -> list[ChatCompletionResponseChoice]:
        """Returns the array of chat completion choices."""
        return self.response.choices

    @property
    def choice(self) -> ChatCompletionResponseChoice:
        """Returns the 0th choice."""
        return self.choices[0]

    @property
    def message(self) -> ChatMessage:
        """Returns the message of the chat completion for the 0th choice."""
        return self.choice.message

    @property
    def content(self) -> str:
        """The content of the chat completion for the 0th choice."""
        content = self.message.content
        # We haven't seen the `list[str]` response type in practice, so for now we
        # return the first item in the list
        return content if isinstance(content, str) else content[0]

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
        return [
            choice.finish_reason if choice.finish_reason else ""
            for choice in self.choices
        ]

    @property
    def tool_calls(self) -> Optional[list[ToolCall]]:
        """Returns the tool calls for the 0th choice message."""
        return self.message.tool_calls

    @property
    def tools(self) -> Optional[list[MistralTool]]:
        """Returns the tools for the 0th choice message.

        Raises:
            ValidationError: if the tool call doesn't match the tool's schema.
        """
        if not self.tool_types or not self.tool_calls or len(self.tool_calls) == 0:
            return None

        if self.choice.finish_reason in ["length", "error"]:
            raise RuntimeError(
                f"Finish reason was {self.choice.finish_reason}, indicating the model "
                "ran out of token or failed (and could not complete the tool call if "
                "trying to)."
            )

        extracted_tools = []
        for tool_call in self.tool_calls:
            for tool_type in self.tool_types:
                if tool_call.function.name == tool_type.name():
                    extracted_tools.append(tool_type.from_tool_call(tool_call))
                    break

        return extracted_tools

    @property
    def tool(self) -> Optional[MistralTool]:
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
        cls, tools_and_outputs: list[tuple[MistralTool, str]]
    ) -> list[ToolMessage]:
        """Returns the tool message parameters for tool call results."""
        return [
            {
                "role": "tool",
                "content": output,
                "tool_call_id": tool.tool_call.id,
                "name": tool.name(),
            }  # type: ignore
            for tool, output in tools_and_outputs
        ]

    @property
    def usage(self) -> UsageInfo:
        """Returns the usage of the chat completion."""
        return self.response.usage

    @property
    def input_tokens(self) -> int:
        """Returns the number of input tokens."""
        return self.usage.prompt_tokens

    @property
    def output_tokens(self) -> Optional[int]:
        """Returns the number of output tokens."""
        return self.usage.completion_tokens

    def dump(self) -> dict[str, Any]:
        """Dumps the response to a dictionary."""
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "output": self.response.model_dump(),
            "cost": self.cost,
        }


class MistralCallResponseChunk(
    BaseCallResponseChunk[ChatCompletionStreamResponse, MistralTool]
):
    """Convenience wrapper around chat completion streaming chunks.

    When using Mirascope's convenience wrappers to interact with Mistral models via
    `MistralCall.stream`, responses will return an `MistralCallResponseChunk`, whereby
    the implemented properties allow for simpler syntax and a convenient developer
    experience.

    Example:

    ```python
    from mirascope.mistral import MistralCall


    class Math(MistralCall):
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

    user_message_param: Optional[Message] = None

    @property
    def choices(self) -> list[ChatCompletionResponseStreamChoice]:
        """Returns the array of chat completion choices."""
        return self.chunk.choices

    @property
    def choice(self) -> ChatCompletionResponseStreamChoice:
        """Returns the 0th choice."""
        return self.choices[0]

    @property
    def delta(self) -> DeltaMessage:
        """Returns the delta of the 0th choice."""
        return self.choice.delta

    @property
    def content(self) -> str:
        """Returns the content of the delta."""
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
        return [
            choice.finish_reason if choice.finish_reason else ""
            for choice in self.choices
        ]

    @property
    def tool_calls(self) -> Optional[list[ToolCall]]:
        """Returns the partial tool calls for the 0th choice message."""
        return self.delta.tool_calls

    @property
    def usage(self) -> Optional[UsageInfo]:
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


class MistralStream(
    BaseStream[
        MistralCallResponseChunk,
        UserMessage,
        AssistantMessage,
        MistralTool,
    ]
):
    """A class for streaming responses from Mistral's API."""

    def __init__(self, stream: Generator[MistralCallResponseChunk, None, None]):
        """Initializes an instance of `MistralStream`."""
        super().__init__(stream, AssistantMessage)


class MistralAsyncStream(
    BaseAsyncStream[
        MistralCallResponseChunk,
        UserMessage,
        AssistantMessage,
        MistralTool,
    ]
):
    """A class for streaming responses from Mistral's API."""

    def __init__(self, stream: AsyncGenerator[MistralCallResponseChunk, None]):
        """Initializes an instance of `MistralAsyncStream`."""
        super().__init__(stream, AssistantMessage)
