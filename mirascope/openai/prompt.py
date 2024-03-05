"""A module for prompting OpenAI's Chat API."""
import datetime
import logging
import os
from typing import (
    Annotated,
    Any,
    AsyncGenerator,
    ClassVar,
    Generator,
    Optional,
    Type,
    TypeVar,
    cast,
)

from openai import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import AfterValidator, BaseModel, ValidationError

from ..base import BasePrompt
from .tools import OpenAITool
from .types import OpenAICallParams, OpenAIChatCompletion, OpenAIChatCompletionChunk
from .utils import convert_tools_list_to_openai_tools, patch_openai_kwargs

logger = logging.getLogger("mirascope")
BaseModelT = TypeVar("BaseModelT", bound=BaseModel)


def _set_api_key(api_key: str) -> None:
    """Sets the OPENAI_API_KEY environment variable."""
    os.environ["OPENAI_API_KEY"] = api_key
    return None


class OpenAIPrompt(BasePrompt):
    '''A class for prompting OpenAI's Chat API.

    Example:

    ```python
    import os

    from mirascope.openai import OpenAIPrompt

    os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


    class BookRecommendation(OpenAIPrompt):
        """
        SYSTEM:
        You're the world's greatest librarian.

        USER:
        Please recommend some {genre} books.
        """

        genre: str


    prompt = BookRecommendation(genre="fantasy")
    print(prompt.create())
    #> There are many great books to read, it ultimately depends...
    ```
    '''

    api_key: Annotated[
        Optional[str],
        AfterValidator(lambda key: _set_api_key(key) if key is not None else None),
    ] = None

    _start_time: Optional[float] = None  # The start time of the completion in ms
    _end_time: Optional[float] = None  # The end time of the completion in ms

    call_params: ClassVar[OpenAICallParams] = OpenAICallParams(
        model="gpt-3.5-turbo-0125",
    )

    @property
    def messages(self) -> list[ChatCompletionMessageParam]:
        """Returns this prompt's list of `ChatCompletionMessageParam` instances."""
        messages = super().messages
        return [cast(ChatCompletionMessageParam, message) for message in messages]

    def create(self) -> OpenAIChatCompletion:
        """Makes a call to the model using this `OpenAIPrompt` instance.

        Returns:
            A `OpenAIChatCompletion` instance.

        Raises:
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        self._start_time = datetime.datetime.now().timestamp() * 1000
        client = OpenAI(base_url=self.call_params.base_url)
        if self.call_params.wrapper is not None:
            client = self.call_params.wrapper(client)
        kwargs: dict[str, Any] = {}
        tools = convert_tools_list_to_openai_tools(self.call_params.tools)
        patch_openai_kwargs(kwargs, self, tools)
        completion = client.chat.completions.create(
            model=self.call_params.model,
            stream=False,
            **kwargs,
        )
        self._end_time = datetime.datetime.now().timestamp() * 1000
        return OpenAIChatCompletion(completion=completion, tool_types=tools)

    async def async_create(self) -> OpenAIChatCompletion:
        """Makes an asynchronous call to the model using this `OpenAIPrompt`.

        Returns:
            An `OpenAIChatCompletion` instance.

        Raises:
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        self._start_time = datetime.datetime.now().timestamp() * 1000
        client = AsyncOpenAI(base_url=self.call_params.base_url)
        if self.call_params.async_wrapper is not None:
            client = self.call_params.async_wrapper(client)
        kwargs: dict[str, Any] = {}
        tools = convert_tools_list_to_openai_tools(self.call_params.tools)
        patch_openai_kwargs(kwargs, self, tools)
        completion = await client.chat.completions.create(
            model=self.call_params.model,
            stream=False,
            **kwargs,
        )
        self._end_time = datetime.datetime.now().timestamp() * 1000
        return OpenAIChatCompletion(completion=completion, tool_types=tools)

    def stream(self) -> Generator[OpenAIChatCompletionChunk, None, None]:
        """Streams the response for a call to the model using `prompt`.

        Yields:
            A `OpenAIChatCompletionChunk` for each chunk of the response.

        Raises:
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        client = OpenAI(base_url=self.call_params.base_url)
        if self.call_params.wrapper is not None:
            client = self.call_params.wrapper(client)
        kwargs: dict[str, Any] = {}
        tools = convert_tools_list_to_openai_tools(self.call_params.tools)
        patch_openai_kwargs(kwargs, self, tools)
        stream = client.chat.completions.create(
            model=self.call_params.model,
            stream=True,
            **kwargs,
        )
        for chunk in stream:
            yield OpenAIChatCompletionChunk(chunk=chunk, tool_types=tools)

    async def async_stream(self) -> AsyncGenerator[OpenAIChatCompletionChunk, None]:
        """Streams the response for an asynchronous call to the model using `prompt`.

        Yields:
            A `OpenAIChatCompletionChunk` for each chunk of the response.

        Raises:
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        client = AsyncOpenAI(base_url=self.call_params.base_url)
        if self.call_params.async_wrapper is not None:
            client = self.call_params.async_wrapper(client)
        kwargs: dict[str, Any] = {}
        tools = convert_tools_list_to_openai_tools(self.call_params.tools)
        patch_openai_kwargs(kwargs, self, tools)
        stream = await client.chat.completions.create(
            model=self.call_params.model,
            stream=True,
            **kwargs,
        )

        async for chunk in stream:
            yield OpenAIChatCompletionChunk(
                chunk=chunk, tool_types=tools if tools else None
            )

    def extract(self, schema: Type[BaseModelT], retries: int = 0) -> BaseModelT:
        """Extracts the given schema from the response of a chat `create` call.

        The given schema is converted into an `OpenAITool`, complete with a description
        of the tool, all of the fields, and their types. This allows us to take
        advantage of OpenAI's tool/function calling functionality to extract information
        from a prompt according to the context provided by the `BaseModel` schema.

        Args:
            schema: The `BaseModel` schema to extract from the completion.
            retries: The maximum number of times to retry the query on validation error.

        Returns:
            The `Schema` instance extracted from the completion.

        Raises:
            AttributeError: if there is no tool in the call creation.
            ValidationError: if the schema cannot be instantiated from the completion.
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        self.call_params.tools = [OpenAITool.from_model(schema)]
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

    async def async_extract(
        self, schema: Type[BaseModelT], retries: int = 0
    ) -> BaseModelT:
        """Extracts the given schema from the response of a chat `create` call.

        The given schema is converted into an `OpenAITool`, complete with a description
        of the tool, all of the fields, and their types. This allows us to take
        advantage of OpenAI's tool/function calling functionality to extract information
        from a prompt according to the context provided by the `BaseModel` schema.

        Args:
            schema: The `BaseModel` schema to extract from the completion.
            retries: The maximum number of times to retry the query on validation error.

        Returns:
            The `Schema` instance extracted from the completion.

        Raises:
            AttributeError: if there is no tool in the call creation.
            ValidationError: if the schema cannot be instantiated from the completion.
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        self.call_params.tools = [OpenAITool.from_model(schema)]
        completion = await self.async_create()
        try:
            model = schema(**completion.tool.model_dump())  # type: ignore
            model._completion = completion
            return model
        except (AttributeError, ValueError, ValidationError) as e:
            if retries > 0:
                logging.info(f"Retrying due to exception: {e}")
                # TODO: update this to include failure history once prompts can handle
                # chat history properly.
                return await self.async_extract(schema, retries - 1)
            raise  # re-raise if we have no retries left
