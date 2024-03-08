"""Types for working with Mistral prompts."""
from typing import Any, Optional, Type, Union

from mistralai.models.chat_completion import (
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatCompletionStreamResponse,
    ChatMessage,
    ToolCall,
    ToolChoice,
)
from pydantic import BaseModel, ConfigDict

from ..base.types import BaseCallParams
from .tools import MistralTool


class MistralChatCompletion(BaseModel):
    """Convenience wrapper for Mistral's chat model completions."""

    completion: ChatCompletionResponse
    tool_types: Optional[list[Type[MistralTool]]] = None
    start_time: float
    end_time: float

    @property
    def choices(self) -> list[ChatCompletionResponseChoice]:
        """Returns the array of chat completion choices."""
        return self.completion.choices

    @property
    def choice(self) -> ChatCompletionResponseChoice:
        """Returns the 0th choice."""
        return self.completion.choices[0]

    @property
    def message(self) -> ChatMessage:
        """Returns the message of the chat completion for the 0th choice."""
        return self.completion.choices[0].message

    @property
    def content(self) -> Union[str, list[str]]:
        """The content of the chat completion for the 0th choice.

        Returns:
            A `str` for regular chat completions, and a `list[str]` if the chat
            completion response format is set to `json_object`
        """
        return self.completion.choices[0].message.content

    # TODO: implement other properties
    # @property
    # def tool_calls(self) -> Optional[list[ChatCompletionMessageToolCall]]:

    # @property
    # def tools(self) -> Optional[list[OpenAITool]]:

    # @property
    # def tool(self) -> Optional[OpenAITool]:

    def dump(self) -> dict[str, Any]:
        """Dumps the chat completion to a dictionary."""
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "output": self.completion.model_dump(),
        }

    def __str__(self):
        """Returns the contained string content for the 0th choice."""
        return self.content if self.content is not None else ""


class MistralCallParams(BaseCallParams):
    """The parameters to use when calling the Mistral API with a prompt."""

    model: str = "open-mixtral-8x7b"
    endpoint: Optional[str] = None
    base_url: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    random_seed: Optional[int] = None
    safe_mode: bool = False
    safe_prompt: bool = False
    tools: Optional[list[Type[MistralTool]]] = None
    tool_choice: Optional[ToolChoice] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)
