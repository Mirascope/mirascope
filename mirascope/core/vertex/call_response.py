"""This module contains the `VertexCallResponse` class.

usage docs: learn/calls.md#handling-responses
"""

from collections.abc import Sequence
from functools import cached_property

from google.cloud.aiplatform_v1beta1.types import GenerateContentResponse
from pydantic import computed_field
from vertexai.generative_models import Content, GenerationResponse, Part, Tool

from .. import BaseMessageParam
from ..base import BaseCallResponse, transform_tool_outputs
from ..base.types import CostMetadata, FinishReason
from ._utils._convert_finish_reason_to_common_finish_reasons import (
    _convert_finish_reasons_to_common_finish_reasons,
)
from ._utils._message_param_converter import VertexMessageParamConverter
from .call_params import VertexCallParams
from .dynamic_config import VertexDynamicConfig
from .tool import VertexTool


class VertexCallResponse(
    BaseCallResponse[
        GenerationResponse,
        VertexTool,
        Tool,
        VertexDynamicConfig,
        Content,
        VertexCallParams,
        Content,
        VertexMessageParamConverter,
    ]
):
    """A convenience wrapper around the Vertex AI `GenerateContentResponse`.

    When calling the Vertex AI API using a function decorated with `vertex_call`, the
    response will be a `VertexCallResponse` instance with properties that allow for
    more convenient access to commonly used attributes.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.vertex import vertex_call


    @vertex_call("gemini-1.5-flash")
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    response = recommend_book("fantasy")  # response is an `VertexCallResponse` instance
    print(response.content)
    ```
    """

    _message_converter: type[VertexMessageParamConverter] = VertexMessageParamConverter

    _provider = "vertex"

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

        vertex does not return model, so we return the model provided by
        the user.
        """
        return self._model

    @computed_field
    @property
    def id(self) -> str | None:
        """Returns the id of the response.

        vertex does not return an id
        """
        return None

    @property
    def usage(self) -> GenerateContentResponse.UsageMetadata:
        """Returns the usage of the chat completion."""
        return self.response.usage_metadata

    @computed_field
    @property
    def input_tokens(self) -> int:
        """Returns the number of input tokens."""
        return self.usage.prompt_token_count

    @computed_field
    @property
    def cached_tokens(self) -> int:
        """Returns the number of cached tokens."""
        return 0

    @computed_field
    @property
    def output_tokens(self) -> int:
        """Returns the number of output tokens."""
        return self.usage.candidates_token_count

    @computed_field
    @cached_property
    def message_param(self) -> Content:
        """Returns the models's response as a message parameter."""
        return Content(role="model", parts=self.response.candidates[0].content.parts)

    @cached_property
    def tools(self) -> list[VertexTool] | None:
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
    def tool(self) -> VertexTool | None:
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
        cls, tools_and_outputs: Sequence[tuple[VertexTool, str]]
    ) -> list[Content]:
        """Returns the tool message parameters for tool call results.

        Args:
            tools_and_outputs: The sequence of tools and their outputs from which the tool
                message parameters should be constructed.

        Returns:
            The list of constructed `Content` from the tool responses.
        """
        return [
            Content(
                role="user",
                parts=[
                    Part.from_function_response(
                        name=tool._name(), response={"result": output}
                    )
                    for tool, output in tools_and_outputs
                ],
            )
        ]

    @property
    def common_finish_reasons(self) -> list[FinishReason] | None:
        return _convert_finish_reasons_to_common_finish_reasons(self.finish_reasons)

    @property
    def common_message_param(self) -> BaseMessageParam:
        return VertexMessageParamConverter.from_provider([self.message_param])[0]

    @property
    def common_user_message_param(self) -> BaseMessageParam | None:
        if not self.user_message_param:
            return None
        return VertexMessageParamConverter.from_provider([self.user_message_param])[0]

    @property
    def cost_metadata(self) -> CostMetadata:
        return super().cost_metadata
