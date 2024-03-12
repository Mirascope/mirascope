"""A module for prompting Google's Gemini Chat API."""
import datetime
import logging
from inspect import isclass
from typing import (
    Annotated,
    Any,
    ClassVar,
    Optional,
    TypeVar,
)

from google.generativeai import GenerativeModel, configure  # type: ignore
from google.generativeai.types import ContentsType  # type: ignore
from pydantic import AfterValidator, BaseModel

from ..base import BaseCall, BasePrompt, BaseType, tool_fn
from .tools import GeminiTool
from .types import (
    GeminiCallParams,
    GeminiCallResponse,
    GeminiCallResponseChunk,
)

logger = logging.getLogger("mirascope")
BaseTypeT = TypeVar("BaseTypeT", bound=BaseType)
BaseModelT = TypeVar("BaseModelT", bound=BaseModel)


class GeminiCall(BaseCall[GeminiCallResponse, GeminiCallResponseChunk], BasePrompt):
    '''A class for prompting Google's Gemini Chat API.

    This prompt supports the message types: USER, MODEL, TOOL

    Example:

    ```python
    from google.generativeai import configure  # type: ignore
    from mirascope.gemini import GeminiPrompt

    configure(api_key="YOUR_API_KEY")


    class BookRecommender(GeminiPrompt):
        template = """
        USER: You're the world's greatest librarian.
        MODEL: Ok, I understand I'm the world's greatest librarian. How can I help?
        USER: Please recommend some {genre} books.

        genre: str


    response = BookRecommender(genre="fantasy").call()
    print(response.call())
    #> As the world's greatest librarian, I am delighted to recommend...
    ```
    '''

    api_key: Annotated[
        Optional[str],
        AfterValidator(lambda key: configure(api_key=key) if key is not None else None),
    ] = None

    call_params: ClassVar[GeminiCallParams] = GeminiCallParams(
        model="gemini-1.0-pro",
        generation_config={"candidate_count": 1},
    )

    @property
    def messages(self) -> ContentsType:
        """Returns the `ContentsType` messages for Gemini `generate_content`.

        Raises:
            ValueError: if the docstring contains an unknown role.
        """
        return self._parse_messages(["model", "user", "tool"])

    def call(self, **kwargs: Any) -> GeminiCallResponse:
        """Makes a call to the model using this `GeminiPrompt`.

        Args:
            **kwargs: Additional keyword arguments that will be used for generating the
                response. These will override any existing argument settings in call
                params.

        Returns:
            A `GeminiCallResponse` instance.
        """
        gemini_pro_model = GenerativeModel(self.call_params.model)
        tools = kwargs.pop("tools") if "tools" in kwargs else []
        if self.call_params.tools:
            tools.extend(self.call_params.tools)
        converted_tools = [
            tool if isclass(tool) else tool_fn(tool)(GeminiTool.from_fn(tool))
            for tool in tools
        ]
        completion_start_time = datetime.datetime.now().timestamp() * 1000
        completion = gemini_pro_model.generate_content(
            self.messages,
            stream=False,
            tools=[tool.tool_schema() for tool in converted_tools]
            if converted_tools
            else None,
            generation_config=self.call_params.generation_config,
            safety_settings=self.call_params.safety_settings,
            request_options=self.call_params.request_options,
        )
        return GeminiCallResponse(
            response=completion,
            tool_types=converted_tools,
            start_time=completion_start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
        )

    # async def async_create(self, **kwargs: Any) -> GeminiCompletion:
    #     """Makes an asynchronous call to the model using this `GeminiPrompt`.

    #     Returns:
    #         An `GeminiCompletion` instance.
    #     """
    #     gemini_pro_model = GenerativeModel(self.call_params.model)
    #     tools = kwargs.pop("tools") if "tools" in kwargs else []
    #     if self.call_params.tools:
    #         tools.extend(self.call_params.tools)
    #     converted_tools = [
    #         tool if isclass(tool) else tool_fn(tool)(GeminiTool.from_fn(tool))
    #         for tool in tools
    #     ]
    #     completion_start_time = datetime.datetime.now().timestamp() * 1000
    #     completion = await gemini_pro_model.generate_content_async(
    #         self.messages,
    #         stream=False,
    #         tools=[tool.tool_schema() for tool in converted_tools]
    #         if converted_tools
    #         else None,
    #         generation_config=self.call_params.generation_config,
    #         safety_settings=self.call_params.safety_settings,
    #         request_options=self.call_params.request_options,
    #     )
    #     return GeminiCompletion(
    #         completion=completion,
    #         tool_types=converted_tools,
    #         start_time=completion_start_time,
    #         end_time=datetime.datetime.now().timestamp() * 1000,
    #     )

    # def stream(self) -> Generator[GeminiCompletionChunk, None, None]:
    #     """Streams the response for a call to the model using this prompt.

    #     Yields:
    #         A `GeminiCompletionChunk` for each chunk of the response.
    #     """
    #     gemini_pro_model = GenerativeModel(self.call_params.model)
    #     completion = gemini_pro_model.generate_content(
    #         self.messages,
    #         stream=True,
    #         generation_config=self.call_params.generation_config,
    #         safety_settings=self.call_params.safety_settings,
    #         request_options=self.call_params.request_options,
    #     )
    #     for chunk in completion:
    #         yield GeminiCompletionChunk(chunk=chunk)

    # async def async_stream(self) -> AsyncGenerator[GeminiCompletionChunk, None]:
    #     """Streams the response for a call to the model using this prompt asynchronously.

    #     Yields:
    #         A `GeminiCompletionChunk` for each chunk of the response.
    #     """
    #     gemini_pro_model = GenerativeModel(self.call_params.model)
    #     completion = await gemini_pro_model.generate_content_async(
    #         self.messages,
    #         stream=True,
    #         generation_config=self.call_params.generation_config,
    #         safety_settings=self.call_params.safety_settings,
    #         request_options=self.call_params.request_options,
    #     )
    #     async for chunk in completion:
    #         yield GeminiCompletionChunk(chunk=chunk)
