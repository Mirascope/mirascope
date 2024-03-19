"""Type classes for interacting with Anthropics's Claude API."""
import xml.etree.ElementTree as ET
from typing import Any, Callable, Literal, Optional, Type, Union, cast

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
        self,
        tool_type: Optional[Type[AnthropicTool]] = None,
        exclude: Optional[set[str]] = None,
    ) -> dict[str, Any]:
        """Returns the keyword argument call parameters."""
        extra_exclude = {"wrapper", "wrapper_async"}
        exclude = extra_exclude if exclude is None else exclude.union(extra_exclude)
        return super().kwargs(tool_type, exclude)


class AnthropicCallResponse(BaseCallResponse[Message, AnthropicTool]):
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
        if (
            not self.tool_types
            or self.response.stop_reason != "stop_sequence"
            or self.response.stop_sequence != "</function_calls>"
        ):
            return None

        try:
            root_node = ET.fromstring(
                f"<wrapper>{self.response.content}</function_calls></wrapper>"
            )
        except ET.ParseError as e:
            raise ValueError("Unable to parse tools from response") from e

        # There must be a <function_calls> tag since we successfully parsed the
        # XML with the manually added </function_calls> tag.
        tool_calls_node = cast(ET.Element, root_node.find("function_calls"))

        extracted_tools = []
        for tool_call_node in tool_calls_node:
            for tool_type in self.tool_types:
                tool_name_node = tool_call_node.find("tool_name")
                if (
                    tool_name_node is not None
                    and tool_name_node.text == tool_type.__name__
                    and (parameters := tool_call_node.find("parameters"))
                ):
                    tool = tool_type.from_tool_call(parameters)
                    extracted_tools.append(tool)
                    break

        return extracted_tools

    @property
    def tool(self) -> Optional[AnthropicTool]:
        """Returns the 0th tool for the 0th choice message."""
        tools = self.tools
        if tools:
            return tools[0]
        return None

    @property
    def content(self) -> str:
        """Returns the string content of the 0th message."""
        return self.response.content[0].text

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
