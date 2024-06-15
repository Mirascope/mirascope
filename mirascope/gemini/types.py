"""Types for interacting with Google's Gemini models using Mirascope."""

from collections.abc import AsyncGenerator, Generator
from typing import Any, Optional, TypeVar, Union

from google.generativeai.protos import FunctionResponse  # type: ignore
from google.generativeai.types import (  # type: ignore
    AsyncGenerateContentResponse,
    ContentDict,
    GenerateContentResponse,
)

from ..base import (
    BaseAsyncStream,
    BaseCallParams,
    BaseCallResponse,
    BaseCallResponseChunk,
    BaseStream,
    BaseTool,
)
from .tools import GeminiTool

BaseToolT = TypeVar("BaseToolT", bound=BaseTool)


class GeminiCallParams(BaseCallParams[GeminiTool]):
    """The parameters to use when calling the Gemini API calls.

    Example:

    ```python
    from mirascope.gemini import GeminiCall, GeminiCallParams


    class BookRecommendation(GeminiPrompt):
        prompt_template = "Please recommend a {genre} book"

        genre: str

        call_params = GeminiCallParams(
            model="gemini-1.0-pro-001",
            generation_config={"candidate_count": 2},
        )


    response = BookRecommender(genre="fantasy").call()
    print(response.content)
    #> The Name of the Wind
    ```
    """

    model: str = "gemini-1.0-pro"
    generation_config: Optional[dict[str, Any]] = {"candidate_count": 1}
    safety_settings: Optional[Any] = None
    request_options: Optional[dict[str, Any]] = None


class GeminiCallResponse(
    BaseCallResponse[
        Union[GenerateContentResponse, AsyncGenerateContentResponse], GeminiTool
    ]
):
    """Convenience wrapper around Gemini's `GenerateContentResponse`.

    When using Mirascope's convenience wrappers to interact with Gemini models via
    `GeminiCall`, responses using `GeminiCall.call()` will return a
    `GeminiCallResponse`, whereby the implemented properties allow for simpler syntax
    and a convenient developer experience.

    Example:

    ```python
    from mirascope.gemini import GeminiPrompt


    class BookRecommender(GeminiPrompt):
        prompt_template = "Please recommend a {genre} book"

        genre: str


    response = BookRecommender(genre="fantasy").call()
    print(response.content)
    #> The Lord of the Rings
    ```
    """

    user_message_param: Optional[ContentDict] = None

    @property
    def message_param(self) -> ContentDict:
        """Returns the models's response as a message parameter."""
        return {"role": "model", "parts": self.response.parts}

    @property
    def tools(self) -> Optional[list[GeminiTool]]:
        """Returns the list of tools for the 0th candidate's 0th content part."""
        if self.tool_types is None:
            return None

        if self.response.candidates[0].finish_reason != 1:  # STOP = 1
            raise RuntimeError(
                "Generation stopped before the stop sequence. "
                "This is likely due to a limit on output tokens that is too low. "
                "Note that this could also indicate no tool is beind called, so we "
                "recommend that you check the output of the call to confirm."
                f"Finish Reason: {self.response.candidates[0].finish_reason}"
            )

        tool_calls = [
            part.function_call for part in self.response.candidates[0].content.parts
        ]

        extracted_tools = []
        for tool_call in tool_calls:
            for tool_type in self.tool_types:
                if tool_call.name == tool_type.name():
                    extracted_tools.append(tool_type.from_tool_call(tool_call))
                    break

        return extracted_tools

    @property
    def tool(self) -> Optional[GeminiTool]:
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
            FunctionResponse(name=tool.name(), response={"result": output})
            for tool, output in tools_and_outputs
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

    def dump(self) -> dict[str, Any]:
        """Dumps the response to a dictionary."""
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "output": str(self.response),
            "cost": self.cost,
        }


class GeminiCallResponseChunk(
    BaseCallResponseChunk[GenerateContentResponse, GeminiTool]
):
    """Convenience wrapper around chat completion streaming chunks.

    When using Mirascope's convenience wrappers to interact with Gemini models via
    `GeminiCall`, responses using `GeminiCall.stream()` will return a
    `GeminiCallResponseChunk`, whereby the implemented properties allow for simpler
    syntax and a convenient developer experience.

    Example:

    ```python
    from mirascope.gemini import GeminiCall


    class Math(GeminiCall):
        prompt_template = "What is 1 + 2?"


    content = ""
    for chunk in Math().stream():
        content += chunk.content
        print(content)
    #> 1
    #  1 +
    #  1 + 2
    #  1 + 2 equals
    #  1 + 2 equals
    #  1 + 2 equals 3
    #  1 + 2 equals 3.
    ```
    """

    user_message_param: Optional[ContentDict] = None

    @property
    def content(self) -> str:
        """Returns the chunk content for the 0th choice."""
        return self.chunk.candidates[0].content.parts[0].text

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
            for candidate in self.chunk.candidates
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


class GeminiStream(
    BaseStream[
        GeminiCallResponseChunk,
        ContentDict,
        ContentDict,
        GeminiTool,
    ]
):
    """A class for streaming responses from Google's Gemini API."""

    def __init__(self, stream: Generator[GeminiCallResponseChunk, None, None]):
        """Initializes an instance of `GeminiStream`."""
        super().__init__(stream, ContentDict)


class GeminiAsyncStream(
    BaseAsyncStream[
        GeminiCallResponseChunk,
        ContentDict,
        ContentDict,
        GeminiTool,
    ]
):
    """A class for streaming responses from Google's Gemini API."""

    def __init__(self, stream: AsyncGenerator[GeminiCallResponseChunk, None]):
        """Initializes an instance of `GeminiAsyncStream`."""
        super().__init__(stream, ContentDict)
