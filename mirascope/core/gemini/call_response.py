"""This module contains the `GeminiCallResponse` class."""

from typing import Optional

from google.generativeai.protos import FunctionCall, FunctionResponse  # type: ignore
from google.generativeai.types import (  # type: ignore
    AsyncGenerateContentResponse,
    ContentDict,
    ContentsType,  # type: ignore
    GenerateContentResponse,
)
from pydantic import computed_field

from ..base import BaseCallResponse
from .call_params import GeminiCallParams
from .dynamic_config import GeminiDynamicConfig
from .tool import GeminiTool


class GeminiCallResponse(
    BaseCallResponse[
        GenerateContentResponse | AsyncGenerateContentResponse,
        GeminiTool,
        GeminiDynamicConfig,
        ContentsType,
        GeminiCallParams,
        ContentDict,
    ]
):
    '''Convenience wrapper around Gemini's `GenerateContentResponse`.

    When using Mirascope's convenience wrappers to interact with Gemini models via
    `GeminiCall`, responses using `GeminiCall.call()` will return a
    `GeminiCallResponse`, whereby the implemented properties allow for simpler syntax
    and a convenient developer experience.

    Example:

    ```python
    from mirascope.core.gemini import gemini_call

    @gemini_call(model="gemini-1.5-pro")
    def recommend_book(genre: str):
        """Recommend a {genre} book."""

    response = recommend_book("fantasy")  # response is an `GeminiCallResponse` instance
    print(response.content)
    #> Sure! I would recommend...
    ```
    '''

    provider: str = "gemini"

    @computed_field
    @property
    def message_param(self) -> ContentDict:
        """Returns the models's response as a message parameter."""
        return {"role": "model", "parts": self.response.parts}

    @computed_field
    @property
    def tools(self) -> list[GeminiTool] | None:
        """Returns the list of tools for the 0th candidate's 0th content part."""
        if self.tool_types is None:
            return None

        if self.finish_reasons[0] != "STOP":
            raise RuntimeError(
                "Generation stopped before the stop sequence. "
                "This is likely due to a limit on output tokens that is too low. "
                "Note that this could also indicate no tool is beind called, so we "
                "recommend that you check the output of the call to confirm."
                f"Finish Reason: {self.finish_reasons[0]}"
            )

        extracted_tools = []
        for tool_call in self.tool_calls:
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
        self, tools_and_outputs: list[tuple[GeminiTool, object]]
    ) -> list[FunctionResponse]:
        """Returns the tool message parameters for tool call results."""
        return [
            FunctionResponse(name=tool._name(), response={"result": output})
            for tool, output in tools_and_outputs
        ]

    @property
    def tool_calls(self) -> list[FunctionCall]:
        """Returns the tool calls for the 0th candidate content."""
        return [
            part.function_call for part in self.response.candidates[0].content.parts
        ]

    @property
    def content(self) -> str:
        """Returns the contained string content for the 0th choice."""
        return self.response.candidates[0].content.parts[0].text

    @property
    def id(self) -> Optional[str]:
        """Returns the id of the response.

        google.generativeai does not return an id
        """
        return None

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
    def model(self) -> None:
        """Returns the model name.

        google.generativeai does not return model, so we return None
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
