"""This module contains the `GeminiCallResponse` class.

usage docs: learn/calls.md#handling-responses
"""

from collections.abc import Sequence
from functools import cached_property

from google.generativeai.protos import FunctionResponse
from google.generativeai.types import (
    AsyncGenerateContentResponse,
    ContentDict,
    ContentsType,  # type: ignore
    GenerateContentResponse,
    Tool,
)
from pydantic import computed_field

from .. import BaseMessageParam
from ..base import BaseCallResponse, transform_tool_outputs
from ..base.types import CostMetadata, FinishReason
from ._utils._convert_finish_reason_to_common_finish_reasons import (
    _convert_finish_reasons_to_common_finish_reasons,
)
from ._utils._message_param_converter import GeminiMessageParamConverter
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
        GeminiMessageParamConverter,
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

    _message_converter: type[GeminiMessageParamConverter] = GeminiMessageParamConverter

    _provider = "gemini"

    @computed_field
    @property
    def content(self) -> str:
        """Returns the contained string content for the 0th choice."""
        return self.response.candidates[0].content.parts[0].text

    @computed_field
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

    @computed_field
    @property
    def model(self) -> str:
        """Returns the model name.

        google.generativeai does not return model, so we return the model provided by
        the user.
        """
        return self._model

    @computed_field
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

    @computed_field
    @property
    def input_tokens(self) -> None:
        """Returns the number of input tokens."""
        return None

    @computed_field
    @property
    def cached_tokens(self) -> None:
        """Returns the number of cached tokens."""
        return None

    @computed_field
    @property
    def output_tokens(self) -> None:
        """Returns the number of output tokens."""
        return None

    @computed_field
    @cached_property
    def message_param(self) -> ContentDict:
        """Returns the models's response as a message parameter."""
        return {"role": "model", "parts": self.response.parts}  # pyright: ignore [reportReturnType]

    @cached_property
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

    @cached_property
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
    @transform_tool_outputs
    def tool_message_params(
        cls, tools_and_outputs: Sequence[tuple[GeminiTool, str]]
    ) -> list[ContentDict]:
        """Returns the tool message parameters for tool call results.

        Args:
            tools_and_outputs: The sequence of tools and their outputs from which the tool
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

    @property
    def common_finish_reasons(self) -> list[FinishReason] | None:
        return _convert_finish_reasons_to_common_finish_reasons(self.finish_reasons)

    @property
    def common_message_param(self) -> BaseMessageParam:
        return GeminiMessageParamConverter.from_provider([self.message_param])[0]

    @property
    def common_user_message_param(self) -> BaseMessageParam | None:
        if not self.user_message_param:
            return None
        return GeminiMessageParamConverter.from_provider([self.user_message_param])[0]

    @computed_field
    @property
    def cost_metadata(self) -> CostMetadata:
        """Get metadata required for cost calculation."""
        return super().cost_metadata
