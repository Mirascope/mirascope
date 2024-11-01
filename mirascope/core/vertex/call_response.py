"""This module contains the `VertexCallResponse` class.

usage docs: learn/calls.md#handling-responses
"""

from google.cloud.aiplatform_v1beta1.types import GenerateContentResponse
from pydantic import computed_field
from vertexai.generative_models import Content, GenerationResponse, Part, Tool

from ..base import BaseCallResponse
from ._utils import calculate_cost
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

    _provider = "vertex"

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

        vertex does not return model, so we return the model provided by
        the user.
        """
        return self._model

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

    @property
    def input_tokens(self) -> int:
        """Returns the number of input tokens."""
        return self.usage.prompt_token_count

    @property
    def output_tokens(self) -> int:
        """Returns the number of output tokens."""
        return self.usage.candidates_token_count

    @property
    def cost(self) -> float | None:
        """Returns the cost of the call."""
        return calculate_cost(self.input_tokens, self.output_tokens, self.model)

    @computed_field
    @property
    def message_param(self) -> Content:
        """Returns the models's response as a message parameter."""
        return Content(role="model", parts=self.response.candidates[0].content.parts)

    @computed_field
    @property
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

    @computed_field
    @property
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
    def tool_message_params(
        cls, tools_and_outputs: list[tuple[VertexTool, object]]
    ) -> list[Content]:
        """Returns the tool message parameters for tool call results.

        Args:
            tools_and_outputs: The list of tools and their outputs from which the tool
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
