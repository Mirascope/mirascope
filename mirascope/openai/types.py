"""Types for interacting with OpenAI models using Mirascope."""

from typing import Any, Callable, Literal, Optional, Type, Union

from httpx import Timeout
from openai import AsyncOpenAI, OpenAI
from openai._types import Body, Headers, Query
from openai.types import Embedding
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessageToolCall,
    ChatCompletionToolChoiceOptionParam,
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
    BaseCallParams,
    BaseCallResponse,
    BaseCallResponseChunk,
)
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

    wrapper: Optional[Callable[[OpenAI], OpenAI]] = None
    wrapper_async: Optional[Callable[[AsyncOpenAI], AsyncOpenAI]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def kwargs(
        self,
        tool_type: Optional[Type[OpenAITool]] = OpenAITool,
        exclude: Optional[set[str]] = None,
    ) -> dict[str, Any]:
        """Returns the keyword argument call parameters."""
        extra_exclude = {"wrapper", "wrapper_async"}
        exclude = extra_exclude if exclude is None else exclude.union(extra_exclude)
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
    def tools(self) -> Optional[list[OpenAITool]]:
        """Returns the tools for the 0th choice message.

        Raises:
            ValidationError: if a tool call doesn't match the tool's schema.
        """
        if not self.tool_types:
            return None

        def reconstruct_tools_from_content() -> list[OpenAITool]:
            # Note: we only handle single tool calls in this case
            tool_type = self.tool_types[0]  # type: ignore
            return [
                tool_type.from_tool_call(
                    ChatCompletionMessageToolCall(
                        id="id",
                        function=Function(
                            name=tool_type.__name__, arguments=self.content
                        ),
                        type="function",
                    )
                )
            ]

        if self.response_format != ResponseFormat(type="json_object"):
            if not self.tool_calls:
                # Let's see if we got an assistant message back instead and try to
                # reconstruct a tool call in this case. We'll assume if it starts with
                # an open curly bracket that we got a tool call assistant message.
                if "{" == self.content[0]:
                    # Note: we only handle single tool calls in JSON mode.
                    return reconstruct_tools_from_content()
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
            return reconstruct_tools_from_content()

        extracted_tools = []
        for tool_call in self.tool_calls:
            for tool_type in self.tool_types:
                if tool_call.function.name == tool_type.__name__:
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


    for chunk in OpenAICall().stream():
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
