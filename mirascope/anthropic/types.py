"""Type classes for interacting with Anthropics's Claude API."""
from typing import Any, Callable, Literal, Optional, Type, Union

from anthropic import Anthropic, AsyncAnthropic
from anthropic._types import Body, Headers, Query
from anthropic.types import (
    ContentBlockDeltaEvent,
    ContentBlockStartEvent,
    Message,
    MessageStreamEvent,
)
from anthropic.types.beta.tools import ToolsBetaMessage
from anthropic.types.completion_create_params import Metadata
from httpx import Timeout
from pydantic import ConfigDict

from ..base.types import BaseCallParams, BaseCallResponse, BaseCallResponseChunk
from .tools import AnthropicTool


class AnthropicCallParams(BaseCallParams[AnthropicTool]):
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

    max_tokens: int = 1000
    model: str = "claude-3-haiku-20240307"
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
        self,
        tool_type: Optional[Type[AnthropicTool]] = None,
        exclude: Optional[set[str]] = None,
    ) -> dict[str, Any]:
        """Returns the keyword argument call parameters."""
        extra_exclude = {"wrapper", "wrapper_async"}
        exclude = extra_exclude if exclude is None else exclude.union(extra_exclude)
        return super().kwargs(tool_type, exclude)


class AnthropicCallResponse(
    BaseCallResponse[Union[Message, ToolsBetaMessage], AnthropicTool]
):
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

    @property
    def tools(self) -> Optional[list[AnthropicTool]]:
        """Returns the tools for the 0th choice message."""
        if not self.tool_types:
            return None

        if self.response.stop_reason != "tool_use":
            raise RuntimeError(
                "Generation stopped with stop reason that is not `tool_use`. "
                "This is likely due to a limit on output tokens that is too low. "
                "Note that this could also indicate no tool is beind called, so we "
                "recommend that you check the output of the call to confirm. "
                f"Stop Reason: {self.response.stop_reason} "
            )

        extracted_tools = []
        for tool_call in self.response.content:
            if tool_call.type != "tool_use":
                continue
            for tool_type in self.tool_types:
                if tool_call.name == tool_type.__name__:
                    tool = tool_type.from_tool_call(tool_call)
                    extracted_tools.append(tool)
                    break

        return extracted_tools

    @property
    def tool(self) -> Optional[AnthropicTool]:
        """Returns the 0th tool for the 0th choice text block."""
        tools = self.tools
        if tools:
            return tools[0]
        return None

    @property
    def content(self) -> str:
        """Returns the string text of the 0th text block."""
        block = self.response.content[0]
        return block.text if block.type == "text" else ""

    def dump(self) -> dict[str, Any]:
        """Dumps the response to a dictionary."""
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "output": self.response.model_dump(),
        }


class AnthropicCallResponseChunk(
    BaseCallResponseChunk[MessageStreamEvent, AnthropicTool]
):
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
