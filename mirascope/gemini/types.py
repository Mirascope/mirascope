"""Type classes for interacting with the OpenAI Chat API."""
from typing import Any, Callable, Optional, Type, Union

from google.generativeai.types import GenerateContentResponse  # type: ignore
from pydantic import BaseModel, ConfigDict

from ..base import BaseCallParams
from .tools import GeminiTool


class GeminiCompletion(BaseModel):
    '''Convenience wrapper around Gemini chat completions.

    When using Mirascope's convenience wrappers to interact with Gemini models via
    `GeminiChat`, responses using `GeminiChat.create()` will return a
    `GeminiCompletion`, whereby the implemented properties allow for simpler syntax
    and a convenient developer experience.

    Example:

    ```python
    from mirascope.gemini import GeminiPrompt


    class BookRecommendation(GeminiPrompt):
        """Please recommend some books."""


    print(BookRecommendation().create())
    ```
    '''

    completion: GenerateContentResponse  # The completion response from the model
    tool_types: Optional[list[Type[GeminiTool]]] = None
    _start_time: Optional[float] = None  # The start time of the completion in ms
    _end_time: Optional[float] = None  # The end time of the completion in ms

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def tool(self) -> Optional[GeminiTool]:
        """Returns the 0th tool for the 0th candidate's 0th content part.

        Raises:
            ValidationError: if the tool call doesn't match the tool's schema.
        """
        if self.tool_types is None:
            return None

        tool_call = self.completion.candidates[0].content.parts[0].function_call
        for tool_type in self.tool_types:
            if tool_call.name == tool_type.__name__:
                return tool_type.from_tool_call(tool_call)

        return None

    def __str__(self):
        """Returns the contained string content for the 0th choice."""
        return self.completion.candidates[0].content.parts[0].text


class GeminiCompletionChunk(BaseModel):
    '''Convenience wrapper around chat completion streaming chunks.

    When using Mirascope's convenience wrappers to interact with Gemini models via
    `GeminiChat`, responses using `GeminiChat.stream()` will return a
    `GeminiCompletionChunk`, whereby the implemented properties allow for simpler
    syntax and a convenient developer experience.

    Example:

    ```python
    from mirascope.gemini import GeminiPrompt


    class BookRecommendation(GeminiPrompt):
        """Please recommend some books.""""""


    for chunk in BookRecommendation().stream():
        print(chunk, end="")
    ```
    '''

    chunk: GenerateContentResponse

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __str__(self) -> str:
        """Returns the chunk content for the 0th choice."""
        return self.chunk.candidates[0].content.parts[0].text


class GeminiCallParams(BaseCallParams):
    '''The parameters to use when calling the Gemini sChat API with a prompt.

    Example:

    ```python
    from mirascope.gemini import GeminiPrompt, GeminiCallParams


    class BookRecommendation(GeminiPrompt):
        """Please recommend some books."""

        call_params = GeminiCallParams(
            model="gemini-1.0-pro-001",
            generation_config={"candidate_count": 2},
        )
    ```
    '''

    model: str = "gemini-pro"
    tools: Optional[list[Union[Callable, Type[GeminiTool]]]] = None
    generation_config: Optional[dict[str, Any]] = None
    safety_settings: Optional[Any] = None
    request_options: Optional[dict[str, Any]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
