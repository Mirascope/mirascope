"""Types for working with Mistral prompts."""
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
)
from pydantic import ConfigDict

from ..base import BaseCallParams, BaseCallResponse, BaseCallResponseChunk
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

        if self.choices[0].finish_reason != "tool_calls":
            raise RuntimeError(
                "Finish reason was not `tool_call`, indicating no or failed tool use."
                "This is likely due to a limit on output tokens that is too low. "
                "Note that this could also indicate no tool is beind called, so we "
                "recommend that you check the output of the call to confirm. "
                f"Finish Reason: {self.choices[0].finish_reason}"
            )

        extracted_tools = []
        for tool_call in self.tool_calls:
            for tool_type in self.tool_types:
                if tool_call.function.name == tool_type.__name__:
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

    def dump(self) -> dict[str, Any]:
        """Dumps the response to a dictionary."""
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "output": self.response.model_dump(),
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


    for chunk in MistralCall().stream():
        print(chunk.content)

    #> 1
    #  +
    #  2
    #   equals
    #
    #  3
    #  .
    ```
    """

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
    def tool_calls(self) -> Optional[list[ToolCall]]:
        """Returns the partial tool calls for the 0th choice message."""
        return self.delta.tool_calls
