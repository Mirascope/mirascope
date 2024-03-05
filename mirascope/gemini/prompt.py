"""A module for prompting Google's Gemini Chat API."""
import datetime
import logging
import re
from inspect import isclass
from typing import Annotated, ClassVar, Generator, Optional, Type, TypeVar

from google.generativeai import GenerativeModel, configure  # type: ignore
from google.generativeai.types import ContentsType  # type: ignore
from pydantic import AfterValidator, BaseModel, ValidationError

from ..base import BasePrompt, format_template, tool_fn
from .tools import GeminiTool
from .types import GeminiCallParams, GeminiCompletion, GeminiCompletionChunk

logger = logging.getLogger("mirascope")
BaseModelT = TypeVar("BaseModelT", bound=BaseModel)


class GeminiPrompt(BasePrompt):
    '''A class for prompting Google's Gemini Chat API.

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

    _start_time: Optional[float] = None  # The start time of the completion in ms
    _end_time: Optional[float] = None  # The end time of the completion in ms

    call_params: ClassVar[GeminiCallParams] = GeminiCallParams(
        model="gemini-1.0-pro",
        generation_config={"candidate_count": 1},
    )

    @property
    def messages(self) -> ContentsType:
        """Returns the `ContentsType` messages for Gemini `generate_content`."""
        messages = []
        for match in re.finditer(
            r"(MODEL|USER|TOOL): " r"((.|\n)+?)(?=\n(MODEL|USER|TOOL):|\Z)",
            self.template(),
        ):
            role = match.group(1).lower()
            content = format_template(self, match.group(2))
            messages.append({"role": role, "parts": [content]})
        if len(messages) == 0:
            messages.append({"role": "user", "parts": [str(self)]})
        return messages

    def create(self) -> GeminiCompletion:
        """Makes a call to the model using this `GeminiPrompt`.

        Returns:
            A `GeminiCompletion` instance.
        """
        self._start_time = datetime.datetime.now().timestamp() * 1000
        gemini_pro_model = GenerativeModel(self.call_params.model)
        tools: Optional[list[Type[GeminiTool]]] = None
        if self.call_params.tools is not None:
            tools = [
                tool if isclass(tool) else tool_fn(tool)(GeminiTool.from_fn(tool))
                for tool in self.call_params.tools
            ]
        completion = gemini_pro_model.generate_content(
            self.messages,
            stream=False,
            tools=[tool.tool_schema() for tool in tools] if tools is not None else None,
            generation_config=self.call_params.generation_config,
            safety_settings=self.call_params.safety_settings,
            request_options=self.call_params.request_options,
        )
        self._end_time = datetime.datetime.now().timestamp() * 1000
        return GeminiCompletion(completion=completion, tool_types=tools)

    def stream(self) -> Generator[GeminiCompletionChunk, None, None]:
        """Streams the response for a call to the model using `prompt`.

        Yields:
            A `GeminiCompletionChunk` for each chunk of the response.
        """
        self._start_time = datetime.datetime.now().timestamp() * 1000
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
        self._end_time = datetime.datetime.now().timestamp() * 1000

    def extract(self, schema: Type[BaseModelT], retries: int = 0) -> BaseModelT:
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
        self.call_params.tools = [GeminiTool.from_model(schema)]
        completion = self.create()
        try:
            model = schema(**completion.tool.model_dump())  # type: ignore
            model._completion = completion
            return model
        except (AttributeError, ValueError, ValidationError) as e:
            if retries > 0:
                logging.info(f"Retrying due to exception: {e}")
                # TODO: update this to include failure history once prompts can handle
                # chat history properly.
                return self.extract(schema, retries - 1)
            raise  # re-raise if we have no retries left
