"""A module for prompting Google's Gemini Chat API."""
import datetime
import logging
import re
from inspect import isclass
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Generator,
    Optional,
    Type,
    TypeVar,
    overload,
)

from google.generativeai import GenerativeModel, configure  # type: ignore
from google.generativeai.types import ContentsType  # type: ignore
from pydantic import AfterValidator, BaseModel, ValidationError

from ..base import BasePrompt, BaseType, format_template, is_base_type, tool_fn
from .tools import GeminiTool
from .types import GeminiCallParams, GeminiCompletion, GeminiCompletionChunk

logger = logging.getLogger("mirascope")
BaseTypeT = TypeVar("BaseTypeT", bound=BaseType)
BaseModelT = TypeVar("BaseModelT", bound=BaseModel)


class GeminiPrompt(BasePrompt):
    '''A class for prompting Google's Gemini Chat API.

    This prompt supports the message types: USER, MODEL, TOOL

    Example:

    ```python
    from google.generativeai import configure  # type: ignore
    from mirascope.gemini import GeminiPrompt

    configure(api_key="YOUR_API_KEY")


    class BookRecommendation(GeminiPrompt):
        """
        USER:
        You're the world's greatest librarian.

        MODEL:
        Ok, I understand that I'm the world's greatest librarian. How can I help you?

        USER:
        Please recommend some {genre} books.
        """

        genre: str


    prompt = BookRecommendation(genre="fantasy")
    print(prompt.create())
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
        messages = []
        for match in re.finditer(
            r"(MODEL|USER|TOOL|[A-Z]*): "
            r"((.|\n)+?)(?=\n(MODEL|USER|TOOL|[A-Z]*):|\Z)",
            self.template(),
        ):
            role = match.group(1).lower()
            if role not in ["model", "user", "tool"]:
                raise ValueError(f"Unknown role: {role}")
            content = format_template(self, match.group(2))
            messages.append({"role": role, "parts": [content]})
        if len(messages) == 0:
            messages.append({"role": "user", "parts": [str(self)]})
        return messages

    def create(self, **kwargs: Any) -> GeminiCompletion:
        """Makes a call to the model using this `GeminiPrompt`.

        Returns:
            A `GeminiCompletion` instance.
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
        return GeminiCompletion(
            completion=completion,
            tool_types=converted_tools,
            start_time=completion_start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
        )

    def stream(self) -> Generator[GeminiCompletionChunk, None, None]:
        """Streams the response for a call to the model using this prompt.

        Yields:
            A `GeminiCompletionChunk` for each chunk of the response.
        """
        gemini_pro_model = GenerativeModel(self.call_params.model)
        completion = gemini_pro_model.generate_content(
            self.messages,
            stream=True,
            generation_config=self.call_params.generation_config,
            safety_settings=self.call_params.safety_settings,
            request_options=self.call_params.request_options,
        )
        for chunk in completion:
            yield GeminiCompletionChunk(chunk=chunk)

    @overload
    def extract(self, schema: Type[BaseTypeT], retries: int = 0) -> BaseTypeT:
        ...  # pragma: no cover

    @overload
    def extract(self, schema: Type[BaseModelT], retries: int = 0) -> BaseModelT:
        ...  # pragma: no cover

    @overload
    def extract(self, schema: Callable, retries: int = 0) -> GeminiTool:
        ...  # pragma: no cover

    def extract(self, schema, retries=0):
        """Extracts the given schema from the response of a chat `create` call.

        The given schema is converted into an `GeminiTool`, complete with a description
        of the tool, all of the fields, and their types. This allows us to take
        advantage of Gemini's tool/function calling functionality to extract information
        from a prompt according to the context provided by the `BaseModel` schema.

        Args:
            schema: The `BaseModel` schema to extract from the completion.
            retries: The maximum number of times to retry the query on validation error.

        Returns:
            The `Schema` instance extracted from the completion.
        """
        return_tool = True
        gemini_tool = schema
        if is_base_type(schema):
            gemini_tool = GeminiTool.from_base_type(schema)
            return_tool = False
        elif not isclass(schema):
            gemini_tool = GeminiTool.from_fn(schema)
        elif not issubclass(schema, GeminiTool):
            gemini_tool = GeminiTool.from_model(schema)
            return_tool = False

        completion = self.create(tools=[gemini_tool])
        try:
            tool = completion.tool
            if tool is None:
                raise AttributeError("No tool found in the completion.")
            if return_tool:
                return tool
            if is_base_type(schema):
                return tool.value
            model = schema(**completion.tool.model_dump())  # type: ignore
            model._completion = completion
            return model
        except (AttributeError, ValueError, ValidationError) as e:
            if retries > 0:
                logging.info(f"Retrying due to exception: {e}")
                # TODO: include failure in retry prompt.
                return self.extract(schema, retries - 1)
            raise  # re-raise if we have no retries left
