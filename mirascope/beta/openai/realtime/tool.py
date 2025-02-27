from __future__ import annotations

from typing import Any, Literal

import jiter
from pydantic.json_schema import SkipJsonSchema
from typing_extensions import NotRequired, TypedDict

from ....core import BaseTool
from ....core.base import GenerateJsonSchemaNoTitles, ToolConfig


class OpenAIRealtimeToolConfig(ToolConfig, total=False):
    """A tool configuration for OpenAI-specific features."""


class RealtimeToolParam(TypedDict, total=False):
    type: Literal["function"]
    """The type of the tool."""

    name: str
    """The name of the function."""

    description: str
    """The description of the function."""

    parameters: NotRequired[dict[str, Any]]
    """Parameters of the function in JSON Schema."""


class FunctionCallArguments(TypedDict, total=False):
    call_id: str
    """The ID of the function call."""

    arguments: str
    """The arguments that the model called."""


class OpenAIRealtimeTool(BaseTool):
    """A class for defining tools for OpenAI Realtime LLM calls.

    Example:

    ```python
    from mirascope.beta.openai import Realtime, OpenAIRealtimeTool, Context

    app = Realtime(
        "gpt-4o-realtime-preview-2024-10-01",
        modalities=["text"],
    )

    def format_book(title: str, author: str) -> str:
        return f"{title} by {author}"

    @app.sender(wait_for_text_response=True, tools=[format_book])
    async def send_genre(context: Context) -> str:
        genre = await async_input("Enter a genre: ")
        return f"Recommend a {genre} book"

    @app.receiver("text")
    async def receive_text(response: str, context: dict[str, Any]) -> None:
        print(f"AI(text): {response}", flush=True)

    @app.receiver("tool")
    def recommend_book(response: OpenAIRealtimeTool, context: Context) -> None:
        print(response.call())
    ```
    """

    __provider__ = "openai"
    __tool_config_type__ = OpenAIRealtimeToolConfig

    tool_call: SkipJsonSchema[FunctionCallArguments]

    @classmethod
    def tool_schema(cls) -> RealtimeToolParam:
        """Constructs a JSON Schema tool schema from the `BaseModel` schema defined.

        Example:
        ```python
        from mirascope.beta.openai import OpenAITool


        def format_book(title: str, author: str) -> str:
            return f"{title} by {author}"


        tool_type = OpenAIRealtimeTool.type_from_fn(format_book)
        print(tool_type.tool_schema())  # prints the OpenAI-specific tool schema
        ```
        """

        tool = RealtimeToolParam(
            name=cls._name(), description=cls._description(), type="function"
        )
        model_schema = cls.model_json_schema(
            schema_generator=GenerateJsonSchemaNoTitles
        )
        if model_schema["properties"]:
            tool["parameters"] = model_schema
        return tool

    @classmethod
    def from_tool_call(cls, tool_call: FunctionCallArguments) -> OpenAIRealtimeTool:
        """Constructs an `OpenAITool` instance from a `tool_call`.

        Args:
            tool_call: The OpenAI tool call from which to construct this tool instance.
        """
        model_json = {"tool_call": tool_call.copy()}
        if args := tool_call.get("arguments", None):
            model_json |= jiter.from_json(args.encode())
        return cls.model_validate(model_json)
