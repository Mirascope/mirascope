"""Types for interacting with Google's Gemini models using Mirascope."""
from typing import Any, Optional, TypeVar

from google.generativeai.types import GenerateContentResponse  # type: ignore

from ..base import BaseCallParams, BaseCallResponse, BaseCallResponseChunk, BaseTool
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


class GeminiCallResponse(BaseCallResponse[GenerateContentResponse, GeminiTool]):
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

    @property
    def tools(self) -> Optional[list[GeminiTool]]:
        """Returns the list of tools for the 0th candidate's 0th content part."""
        if self.tool_types is None:
            return None

        tool_calls = [
            part.function_call for part in self.response.candidates[0].content.parts
        ]

        extracted_tools = []
        for tool_call in tool_calls:
            for tool_type in self.tool_types:
                if tool_call.name == tool_type.__name__:
                    extracted_tools.append(tool_type.from_tool_call(tool_call))
                    break

        return extracted_tools

    @property
    def tool(self) -> Optional[GeminiTool]:
        """Returns the 0th tool for the 0th candidate's 0th content part.

        Raises:
            ValidationError: if the tool call doesn't match the tool's schema.
        """
        if self.tool_types is None:
            return None

        tool_call = self.response.candidates[0].content.parts[0].function_call
        for tool_type in self.tool_types:
            if tool_call.name == tool_type.__name__:
                return tool_type.from_tool_call(tool_call)

        return None

    @property
    def content(self) -> str:
        """Returns the contained string content for the 0th choice."""
        return self.response.candidates[0].content.parts[0].text

    def dump(self) -> dict[str, Any]:
        """Dumps the response to a dictionary."""
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "output": str(self.response),
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


    class BookRecommender(GeminiCall):
        prompt_template = "Please recommend a {genre} book"

        genre: str


    for chunk in BookRecommender(genre="science fiction").stream():
        print(chunk)

    #> D
    #  u
    #
    #  ne
    #
    #  by F
    #  r
    #  an
    #  k
    #  .
    ```
    """

    @property
    def content(self) -> str:
        """Returns the chunk content for the 0th choice."""
        return self.chunk.candidates[0].content.parts[0].text
