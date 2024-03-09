"""Type classes for interacting with Anthropics's Chat API."""
from typing import Any, Callable, Literal, Optional, Union

from anthropic import Anthropic, AsyncAnthropic
from anthropic._types import Body, Headers, Query
from anthropic.types import (
    ContentBlockDeltaEvent,
    ContentBlockStartEvent,
    Message,
    MessageStreamEvent,
)
from anthropic.types.completion_create_params import Metadata
from httpx import Timeout
from pydantic import BaseModel, ConfigDict

from ..base.types import BaseCallParams


class AnthropicCompletion(BaseModel):
    '''Convenience wrapper around Anthropic chat completions.

    When using Mirascope's convenience wrappers to interact with Anthropic models via
    `AnthropicPrompt`, responses using `AnthropicPrompt.create()` will return a
    `AnthropicCompletion`, whereby the implemented properties allow for simpler syntax
    and a convenient developer experience.

    Example:

    ```python
    from mirascope.anthropic import AnthropicPrompt


    class BookRecommendation(AnthropicPrompt):
        """Please recommend some books."""


    print(BookRecommendation().create())
    ```
    '''

    completion: Message
    start_time: float  # The start time of the completion in ms
    end_time: float  # The end time of the completion in ms

    def __str__(self) -> str:
        """Returns the string content of the 0th message."""
        return self.completion.content[0].text


class AnthropicCompletionChunk(BaseModel):
    '''Convenience wrapper around Anthropic chat completion streaming chunks.

    When using Mirascope's convenience wrappers to interact with Anthropic models via
    `AnthropicPrompt`, responses using `AnthropicPrompt.stream()` will return a
    `AnthropicCompletionChunk`, whereby the implemented properties allow for simpler
    syntax and a convenient developer experience.

    Example:

    ```python
    from mirascope.anthropic import AnthropicPrompt


    class BookRecommendation(AnthropicPrompt):
        """Please recommend some books.""""""


    for chunk in BookRecommendation().stream():
        print(chunk, end="")
    ```
    '''

    chunk: MessageStreamEvent

    @property
    def type(
        self,
    ) -> Literal[
        "message_start",
        "message_delta",
        "message_stop",
        "content_block_start",
        "content_block_delta",
        "content_block_stop",
    ]:
        """Returns the type of the chunk."""
        return self.chunk.type

    def __str__(self) -> str:
        """Returns the string content of the 0th message."""
        if isinstance(self.chunk, ContentBlockStartEvent):
            return self.chunk.content_block.text
        if isinstance(self.chunk, ContentBlockDeltaEvent):
            return self.chunk.delta.text
        return ""


class AnthropicCallParams(BaseCallParams):
    '''The parameters to use when calling d Claud API with a prompt.

    Example:

    ```python
    from mirascope.anthropic import AnthropicPrompt, AnthropicCallParams


    class BookRecommendation(AnthropicPrompt):
        """Please recommend some books."""

        call_params = AnthropicCallParams(
            model="anthropic-3-opus-20240229",
        )
    ```
    '''

    base_url: Optional[str] = None
    wrapper: Optional[Callable[[Anthropic], Anthropic]] = None
    async_wrapper: Optional[Callable[[AsyncAnthropic], AsyncAnthropic]] = None
    max_tokens: int = 1000
    model: str = "claude-3-sonnet-20240229"
    metadata: Optional[Metadata] = None
    stop_sequences: Optional[list[str]] = None
    system: Optional[str] = None
    temperature: Optional[float] = None
    top_k: Optional[int] = None
    top_p: Optional[float] = None
    extra_headers: Optional[Headers] = None
    extra_query: Optional[Query] = None
    extra_body: Optional[Body] = None
    timeout: Optional[Union[float, Timeout]] = 600

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def kwargs(self) -> dict[str, Any]:
        """Returns the keyword argument call parameters."""
        return {
            key: value
            for key, value in self.model_dump(
                exclude={"base_url", "wrapper", "async_wrapper", "tools"}
            ).items()
            if value is not None
        }


params = AnthropicCallParams()
