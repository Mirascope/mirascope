"""Types for interacting with Groq's Cloud API using Mirascope."""
from typing import Any, Callable, Optional, Type, Union

from groq import AsyncGroq, Groq
from groq._types import Body, Headers, Query
from groq.lib.chat_completion_chunk import (
    ChatCompletionChunk,
    ChoiceDelta,
    ChoiceDeltaToolCall,
)
from groq.lib.chat_completion_chunk import Choice as ChunkChoice
from groq.types.chat import ChatCompletion
from groq.types.chat.chat_completion import (
    Choice,
    ChoiceMessage,
    ChoiceMessageToolCall,
    ChoiceMessageToolCallFunction,
    Usage,
)
from groq.types.chat.completion_create_params import ResponseFormat, ToolChoice
from httpx import Timeout
from pydantic import ConfigDict

from ..base import BaseCallParams, BaseCallResponse, BaseCallResponseChunk
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
    tool_choice: Optional[ToolChoice] = None
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

    wrapper: Optional[Callable[[Groq], Groq]] = None
    wrapper_async: Optional[Callable[[AsyncGroq], AsyncGroq]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def kwargs(
        self,
        tool_type: Optional[Type[GroqTool]] = GroqTool,
        exclude: Optional[set[str]] = None,
    ) -> dict[str, Any]:
        """Returns the keyword argument call parameters."""
        extra_exclude = {"wrapper", "wrapper_async"}
        exclude = extra_exclude if exclude is None else exclude.union(extra_exclude)
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

    @property
    def choices(self) -> list[Choice]:
        """Returns the array of chat completion choices."""
        return self.response.choices

    @property
    def choice(self) -> Choice:
        """Returns the 0th choice."""
        return self.choices[0]

    @property
    def message(self) -> ChoiceMessage:
        """Returns the message of the chat completion for the 0th choice."""
        return self.choice.message

    @property
    def content(self) -> str:
        """Returns the content of the chat completion for the 0th choice."""
        return self.message.content if self.message.content is not None else ""

    @property
    def tool_calls(self) -> Optional[list[ChoiceMessageToolCall]]:
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

        if self.response_format != ResponseFormat(type="json_object"):
            if not self.tool_calls:
                return None

            if self.choices[0].finish_reason not in ["tool_calls", "function_call"]:
                raise RuntimeError(
                    "Finish reason was not `tool_calls` or `function_call`, indicating "
                    "no or failed tool use. This is likely due to a limit on output "
                    "tokens that is too low. Note that this could also indicate no "
                    "tool is beind called, so we recommend that you check the output "
                    "of the call to confirm. "
                    f"Finish Reason: {self.choices[0].finish_reason}"
                )
        else:
            # Note: we only handle single tool calls in JSON mode.
            tool_type = self.tool_types[0]
            return [
                tool_type.from_tool_call(
                    ChoiceMessageToolCall(
                        id="id",
                        function=ChoiceMessageToolCallFunction(
                            name=tool_type.__name__, arguments=self.content
                        ),
                        type="function",
                    )
                )
            ]

        extracted_tools = []
        for tool_call in self.tool_calls:
            for tool_type in self.tool_types:
                if tool_call.function and tool_call.function.name == tool_type.__name__:
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

    @property
    def usage(self) -> Optional[Usage]:
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


    for chunk in Math().stream():
        print(chunk.content)

    #> 1
    #  +
    #  2
    #   equals
    #
    #  3
    #  .
    """

    response_format: Optional[ResponseFormat] = None

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
    def tool_calls(self) -> Optional[list[ChoiceDeltaToolCall]]:
        """Returns the partial tool calls for the 0th choice message.

        The first `list[ChoiceDeltaToolCall]` will contain the name of the tool and
        index, and subsequent `list[ChoiceDeltaToolCall]`s will contain the arguments
        which will be strings that need to be concatenated with future
        `list[ChoiceDeltaToolCall]`s to form a complete JSON tool calls. The last
        `list[ChoiceDeltaToolCall]` will be None indicating end of stream.
        """
        return self.delta.tool_calls
