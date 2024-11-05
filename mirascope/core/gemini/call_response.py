"""This module contains the `GeminiCallResponse` class.

usage docs: learn/calls.md#handling-responses
"""

from google.generativeai.protos import FunctionResponse
from google.generativeai.types import (
    AsyncGenerateContentResponse,
    ContentDict,
    ContentsType,  # type: ignore
    GenerateContentResponse,
    Tool,
)
from pydantic import computed_field

from ..base import BaseCallResponse
from ._utils import calculate_cost
from .call_params import GeminiCallParams
from .dynamic_config import GeminiDynamicConfig
from .tool import GeminiTool


class GeminiCallResponse(
    BaseCallResponse[
        GenerateContentResponse | AsyncGenerateContentResponse,
        GeminiTool,
        Tool,
        GeminiDynamicConfig,
        ContentsType,
        GeminiCallParams,
        ContentDict,
    ]
):
    """A convenience wrapper around the Gemini API response.

    When calling the Gemini API using a function decorated with `gemini_call`, the
    response will be a `GeminiCallResponse` instance with properties that allow for
    more convenient access to commonly used attributes.


    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.gemini import gemini_call


    @gemini_call("gemini-1.5-flash")
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    response = recommend_book("fantasy")  # response is an `GeminiCallResponse` instance
    print(response.content)
    ```
    """

    _provider = "gemini"

    @property
    def content(self) -> str:
        """Returns the contained string content for the 0th choice."""
        return self.response.candidates[0].content.parts[0].text

    @property
    def finish_reasons(self) -> list[str]:
        """Returns the finish reasons of the response."""
        finish_reasons = [
            "FINISH_REASON_UNSPECIFIED",
            "STOP",
            "MAX_TOKENS",
            "SAFETY",
            "RECITATION",
            "OTHER",
        ]

        return [
            finish_reasons[candidate.finish_reason]
            for candidate in self.response.candidates
        ]

    @property
    def model(self) -> str:
        """Returns the model name.

        google.generativeai does not return model, so we return the model provided by
        the user.
        """
        return self._model

    @property
    def id(self) -> str | None:
        """Returns the id of the response.

        google.generativeai does not return an id
        """
        return None

    @property
    def usage(self) -> None:
        """Returns the usage of the chat completion.

        google.generativeai does not have Usage, so we return None
        """
        return None

    @property
    def input_tokens(self) -> None:
        """Returns the number of input tokens."""
        return None

    @property
    def output_tokens(self) -> None:
        """Returns the number of output tokens."""
        return None

    @property
    def cost(self) -> float | None:
        """Returns the cost of the call."""
        return calculate_cost(self.input_tokens, self.output_tokens, self.model)

    @computed_field
    @property
    def message_param(self) -> ContentDict:
        """Returns the models's response as a message parameter."""
        return {"role": "model", "parts": self.response.parts}  # pyright: ignore [reportReturnType]

    @computed_field
    @property
    def tools(self) -> list[GeminiTool] | None:
        """Returns the list of tools for the 0th candidate's 0th content part."""
        if self.tool_types is None:
            return None

        extracted_tools = []
        for part in self.response.candidates[0].content.parts:
            tool_call = part.function_call
            for tool_type in self.tool_types:
                if tool_call.name == tool_type._name():
                    extracted_tools.append(tool_type.from_tool_call(tool_call))
                    break

        return extracted_tools

    @computed_field
    @property
    def tool(self) -> GeminiTool | None:
        """Returns the 0th tool for the 0th candidate's 0th content part.

        Raises:
            ValidationError: if the tool call doesn't match the tool's schema.
        """
        tools = self.tools
        if tools:
            return tools[0]
        return None

    @classmethod
    def tool_message_params(
        cls, tools_and_outputs: list[tuple[GeminiTool, object]]
    ) -> list[ContentDict]:
        """Returns the tool message parameters for tool call results.

        Args:
            tools_and_outputs: The list of tools and their outputs from which the tool
                message parameters should be constructed.

        Returns:
            The list of constructed `FunctionResponse` parameters.
        """
        return [
            {
                "role": "user",
                "parts": [
                    FunctionResponse(name=tool._name(), response={"result": output})
                    for tool, output in tools_and_outputs
                ],
            }
        ]
