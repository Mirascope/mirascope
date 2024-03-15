"""Type classes for interacting with Anthropics's Claude API."""
from typing import Annotated, Any, Callable, Literal, Optional, Union

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
from pydantic import BeforeValidator, ConfigDict, InstanceOf

from ..base.types import BaseCallParams, BaseCallResponse, BaseCallResponseChunk


class AnthropicCallParams(BaseCallParams[Any]):
    """The parameters to use when calling d Claud API with a prompt.

    Example:

    ```python
    from mirascope.anthropic import AnthropicCall, AnthropicCallParams


    class BookRecommender(AnthropicCall):
        prompt_template = "Please recommend some books."

        call_params = AnthropicCallParams(
            model="anthropic-3-opus-20240229",
        )
    ```
    """

    # TOOLS ARE NOT YET SUPPORTED
    tools: Annotated[InstanceOf[None], BeforeValidator(lambda x: None)] = None

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

    wrapper: Optional[Callable[[Anthropic], Anthropic]] = None
    wrapper_async: Optional[Callable[[AsyncAnthropic], AsyncAnthropic]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def kwargs(
        self, tool_type: Optional[Any] = None, exclude: Optional[set[str]] = None
    ) -> dict[str, Any]:
        """Returns the keyword argument call parameters."""
        extra_exclude = {"wrapper", "wrapper_async"}
        exclude = extra_exclude if exclude is None else exclude.union(extra_exclude)
        return super().kwargs(tool_type, exclude)


class AnthropicCallResponse(BaseCallResponse[Message, Any]):
    """Convenience wrapper around the Anthropic Claude API.

    When using Mirascope's convenience wrappers to interact with Anthropic models via
    `AnthropicCall`, responses using `Anthropic.call()` will return an
    `AnthropicCallResponse`, whereby the implemented properties allow for simpler syntax
    and a convenient developer experience.

    Example:

    ```python
    from mirascope.anthropic import AnthropicCall


    class BookRecommender(AnthropicCall):
        prompt_template = "Please recommend some books."


    print(BookRecommender().call())
    ```
    """

    # TOOLS NOT YET SUPPORTED
    tool_types: Annotated[InstanceOf[None], BeforeValidator(lambda x: None)] = None

    @property
    def tools(self) -> None:
        """Returns the tools for the 0th choice message.

        NOT YET IMPLEMENTED. Required for abstract base class, but this will always
        return None until implemented.
        """
        return None

    @property
    def tool(self) -> None:
        """Returns the 0th tool for the 0th choice message.

        NOT YET IMPLEMENTED. Required for abstract base class, but this will always
        return None until implemented.
        """
        return None

    @property
    def content(self) -> str:
        """Returns the string content of the 0th message."""
        return self.response.content[0].text


class AnthropicCallResponseChunk(BaseCallResponseChunk[MessageStreamEvent, Any]):
    """Convenience wrapper around the Anthropic API streaming chunks.

    When using Mirascope's convenience wrappers to interact with Anthropic models via
    `AnthropicCall`, responses using `AnthropicCall.stream()` will yield
    `AnthropicCallResponseChunk`, whereby the implemented properties allow for simpler
    syntax and a convenient developer experience.

    Example:

    ```python
    from mirascope.anthropic import AnthropicCall


    class BookRecommender(AnthropicCall):
        prompt_template = "Please recommend some books."


    for chunk in BookRecommender().stream():
        print(chunk, end="")
    ```
    """

    # TOOLS NOT YET SUPPORTED
    tool_types: Annotated[InstanceOf[None], BeforeValidator(lambda x: None)] = None

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

    @property
    def content(self) -> str:
        """Returns the string content of the 0th message."""
        if isinstance(self.chunk, ContentBlockStartEvent):
            return self.chunk.content_block.text
        if isinstance(self.chunk, ContentBlockDeltaEvent):
            return self.chunk.delta.text
        return ""
