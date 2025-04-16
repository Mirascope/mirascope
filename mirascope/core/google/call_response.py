"""This module contains the `GoogleCallResponse` class.

usage docs: learn/calls.md#handling-responses
"""

from collections.abc import Sequence
from functools import cached_property

from google.genai.types import (
    ContentDict,
    ContentListUnion,
    ContentListUnionDict,
    FunctionResponseDict,
    GenerateContentResponse,
    GenerateContentResponseUsageMetadata,
    PartDict,
    # Import manually SchemaDict to avoid Pydantic error
    SchemaDict,  # noqa: F401
    Tool,
)
from pydantic import computed_field

from .. import BaseMessageParam
from ..base import BaseCallResponse, transform_tool_outputs
from ..base.types import CostMetadata, FinishReason, GoogleMetadata
from ._utils._convert_finish_reason_to_common_finish_reasons import (
    _convert_finish_reasons_to_common_finish_reasons,
)
from ._utils._message_param_converter import GoogleMessageParamConverter
from .call_params import GoogleCallParams
from .dynamic_config import GoogleDynamicConfig
from .tool import GoogleTool


class GoogleCallResponse(
    BaseCallResponse[
        GenerateContentResponse,
        GoogleTool,
        Tool,
        GoogleDynamicConfig,
        ContentListUnion | ContentListUnionDict,
        GoogleCallParams,
        ContentDict,
        GoogleMessageParamConverter,
    ]
):
    """A convenience wrapper around the Google API response.

    When calling the Google API using a function decorated with `google_call`, the
    response will be a `GoogleCallResponse` instance with properties that allow for
    more convenient access to commonly used attributes.


    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.google import google_call


    @google_call("google-1.5-flash")
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    response = recommend_book("fantasy")  # response is an `GoogleCallResponse` instance
    print(response.content)
    ```
    """

    _message_converter: type[GoogleMessageParamConverter] = GoogleMessageParamConverter

    _provider = "google"

    @computed_field
    @property
    def content(self) -> str:
        """Returns the contained string content for the 0th choice."""
        return self.response.candidates[0].content.parts[0].text  # pyright: ignore [reportOptionalSubscript, reportReturnType, reportOptionalMemberAccess, reportOptionalIterable]

    @computed_field
    @property
    def finish_reasons(self) -> list[str]:
        """Returns the finish reasons of the response."""

        return [
            candidate.finish_reason.value
            for candidate in (self.response.candidates or [])
            if candidate and candidate.finish_reason is not None
        ]

    @computed_field
    @property
    def model(self) -> str:
        """Returns the model name.

        google.generativeai does not return model, so we return the model provided by
        the user.
        """
        return (
            self.response.model_version if self.response.model_version else self._model
        )

    @computed_field
    @property
    def id(self) -> str | None:
        """Returns the id of the response.

        google.generativeai does not return an id
        """
        return None

    @property
    def usage(self) -> GenerateContentResponseUsageMetadata | None:
        """Returns the usage of the chat completion.

        google.generativeai does not have Usage, so we return None
        """
        return self.response.usage_metadata

    @computed_field
    @property
    def input_tokens(self) -> int | None:
        """Returns the number of input tokens."""
        return (
            self.response.usage_metadata.prompt_token_count
            if self.response.usage_metadata
            else None
        )

    @computed_field
    @property
    def cached_tokens(self) -> int | None:
        """Returns the number of cached tokens."""
        return (
            self.response.usage_metadata.cached_content_token_count
            if self.response.usage_metadata
            else None
        )

    @computed_field
    @property
    def output_tokens(self) -> int | None:
        """Returns the number of output tokens."""
        return (
            self.response.usage_metadata.candidates_token_count
            if self.response.usage_metadata
            else None
        )

    @computed_field
    @cached_property
    def message_param(self) -> ContentDict:
        """Returns the models's response as a message parameter."""
        return {"role": "model", "parts": self.response.candidates[0].content.parts}  # pyright: ignore [reportReturnType, reportOptionalSubscript, reportOptionalMemberAccess]

    @cached_property
    def tools(self) -> list[GoogleTool] | None:
        """Returns the list of tools for the response."""
        if self.tool_types is None:
            return None

        extracted_tools = []
        for tool_call in self.response.function_calls or []:
            for tool_type in self.tool_types:
                if tool_call.name == tool_type._name():  # pyright: ignore [reportOptionalMemberAccess]
                    extracted_tools.append(tool_type.from_tool_call(tool_call))  # pyright: ignore [reportArgumentType]
                    break

        return extracted_tools

    @cached_property
    def tool(self) -> GoogleTool | None:
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
        cls, tools_and_outputs: Sequence[tuple[GoogleTool, str]]
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
                    PartDict(
                        function_response=FunctionResponseDict(
                            name=tool._name(), response={"result": output}
                        )
                    )
                    for tool, output in tools_and_outputs
                ],
            }
        ]

    @property
    def common_finish_reasons(self) -> list[FinishReason] | None:
        return _convert_finish_reasons_to_common_finish_reasons(self.finish_reasons)

    @property
    def common_message_param(self) -> BaseMessageParam:
        return GoogleMessageParamConverter.from_provider([self.message_param])[0]

    @property
    def common_user_message_param(self) -> BaseMessageParam | None:
        if not self.user_message_param:
            return None
        return GoogleMessageParamConverter.from_provider([self.user_message_param])[0]

    @property
    def cost_metadata(self) -> CostMetadata:
        cost_metadata = super().cost_metadata
        cost_metadata.google = GoogleMetadata(
            use_vertex_ai="use_vertex_ai" in self.metadata.get("tags", [])
        )
        return cost_metadata
