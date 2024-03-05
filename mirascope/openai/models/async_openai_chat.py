"""Class for interacting with AsyncOpenAI through Chat APIs."""
import datetime
import logging
import warnings
from typing import Any, AsyncGenerator, Callable, Optional, Type, TypeVar, Union

from openai import AsyncOpenAI
from pydantic import BaseModel, ValidationError

from ...base import BasePrompt, convert_base_model_to_tool
from ..tools import OpenAITool
from ..types import OpenAIChatCompletion, OpenAIChatCompletionChunk
from ..utils import (
    convert_tools_list_to_openai_tools,
    patch_openai_kwargs,
)

warnings.filterwarnings("always", category=DeprecationWarning, module="mirascope")
logger = logging.getLogger("mirascope")
BaseModelT = TypeVar("BaseModelT", bound=BaseModel)


class AsyncOpenAIChat:
    '''A convenience wrapper for the AsyncOpenAI Chat client.

    The Mirascope convenience wrapper for OpenAI provides a more user-friendly interface
    for interacting with their API. For more usage details, check out our examples.

    Example:

    ```python
    import asyncio
    import os

    from mirascope import AsyncOpenAIChat, BasePrompt

    os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

    class BookRecommendationPrompt(BasePrompt):
        """
        Can you recommend some books on {topic}?
        """

        topic: str


    prompt = BookRecommendationPrompt(topic="how to bake a cake")

    model = AsyncOpenAIChat()


    async def create_book_recommendation():
        """Asynchronously creates the response for a call to the model using `prompt`."""
        return await model.create(prompt)


    print(asyncio.run(create_book_recommendation()))
    #> Certinly! Here are some books on how to bake a cake:
    #  1. "The Cake Bible" by Rose Levy Beranbaum
    #  2. "Joy of Baking" by Irma S Rombauer and Marion Rombauer Becker
    #  ...
    ```
    '''

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        client_wrapper: Optional[Callable] = None,
        **kwargs: Any,
    ):
        """Initializes an instance of `AsyncOpenAIChat."""
        warnings.warn(
            "`AsyncOpenAIChat` is deprecated. Use `OpenAIPrompt` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        if "model" in kwargs:
            self.model = kwargs.pop("model")
            self.model_is_set = True
        else:
            self.model = "gpt-3.5-turbo"
            self.model_is_set = False
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url, **kwargs)
        if client_wrapper is not None:
            self.client = client_wrapper(self.client)

    async def create(
        self,
        prompt: Optional[Union[BasePrompt, str]] = None,
        tools: Optional[list[Union[Callable, Type[OpenAITool]]]] = None,
        **kwargs: Any,
    ) -> OpenAIChatCompletion:
        """Asynchronously makes a call to the model using `prompt`.

        Args:
            prompt: The prompt to use for the call. This can either be a `BasePrompt`
                instance, a raw string, or `None`. If `prompt` is `None`, then the call
                will attempt to use the `messages` keyword argument.
            tools: A list of `OpenAITool` types or `Callable` functions that the
                creation call can decide to use. If `tools` is provided, `tool_choice`
                will be set to `auto` unless manually specified.
            **kwargs: Additional keyword arguments to pass to the API call. You can
                find available keyword arguments here:
                https://platform.openai.com/docs/api-reference/chat/create

        Returns:
            A `OpenAIChatCompletion` instance.

        Raises:
            ValueError: if neither `prompt` nor `messages` are provided.
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        extract = kwargs.pop("extract") if "extract" in kwargs else False
        if isinstance(prompt, BasePrompt):
            if self.model_is_set:
                warnings.warn(
                    "The `model` parameter will be ignored when `prompt` is of type "
                    "`BasePrompt` in favor of `OpenAICallParams.model` field inside of "
                    "`prompt`; version>=0.3.0. Use `OpenAICallParams` inside of your "
                    "`BasePrompt` instead.",
                    DeprecationWarning,
                    stacklevel=2,
                )
            self.model = prompt.call_params.model

            if tools is not None and not extract:
                warnings.warn(
                    "The `tools` parameter is deprecated; version>=0.3.0. "
                    "Use `OpenAICallParams` inside of your `BasePrompt` instead.",
                    DeprecationWarning,
                    stacklevel=2,
                )
            if prompt.call_params.tools is not None:
                tools = prompt.call_params.tools

        start_time = datetime.datetime.now().timestamp() * 1000
        openai_tools = convert_tools_list_to_openai_tools(tools)
        patch_openai_kwargs(kwargs, prompt, openai_tools)

        completion = OpenAIChatCompletion(
            completion=await self.client.chat.completions.create(
                model=self.model,
                stream=False,
                **kwargs,
            ),
            tool_types=openai_tools if tools else None,
        )
        completion._start_time = start_time
        completion._end_time = datetime.datetime.now().timestamp() * 1000
        return completion

    async def stream(
        self,
        prompt: Optional[Union[BasePrompt, str]] = None,
        tools: Optional[list[Union[Callable, Type[OpenAITool]]]] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[OpenAIChatCompletionChunk, None]:
        """Asynchronously streams the response for a call to the model using `prompt`.

        Args:
            prompt: The `BasePrompt` to use for the call.
            tools: A list of `OpenAITool` types or `Callable` functions that the
                creation call can decide to use. If `tools` is provided, `tool_choice`
                will be set to `auto` unless manually specified.
            **kwargs: Additional keyword arguments to pass to the API call. You can
                find available keyword arguments here:
                https://platform.openai.com/docs/api-reference/prompts/create

        Yields:
            A `OpenAIChatCompletionChunk` for each chunk of the response.

        Raises:
            ValueError: if neither `prompt` nor `messages` are provided.
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        if isinstance(prompt, BasePrompt):
            if self.model_is_set:
                warnings.warn(
                    "The `model` parameter will be ignored when `prompt` is of type "
                    "`BasePrompt` in favor of `OpenAICallParams.model` field inside of "
                    "`prompt`; version>=0.3.0. Use `OpenAICallParams` inside of your "
                    "`BasePrompt` instead.",
                    DeprecationWarning,
                    stacklevel=2,
                )
            self.model = prompt.call_params.model

            if tools is not None:
                warnings.warn(
                    "The `tools` parameter is deprecated; version>=0.3.0. "
                    "Use `OpenAICallParams` inside of your `BasePrompt` instead.",
                    DeprecationWarning,
                    stacklevel=2,
                )
            if prompt.call_params.tools is not None:
                tools = prompt.call_params.tools

        openai_tools = convert_tools_list_to_openai_tools(tools)
        patch_openai_kwargs(kwargs, prompt, openai_tools)

        completion_stream = await self.client.chat.completions.create(
            model=self.model,
            stream=True,
            **kwargs,
        )

        async for chunk in completion_stream:
            yield OpenAIChatCompletionChunk(
                chunk=chunk, tool_types=openai_tools if tools else None
            )

    async def extract(
        self,
        schema: Type[BaseModelT],
        prompt: Optional[Union[BasePrompt, str]] = None,
        retries: int = 0,
        **kwargs: Any,
    ) -> BaseModelT:
        """Extracts the given schema from the response of a chat `create` call async.

        The given schema is converted into an `OpenAITool`, complete with a description
        of the tool, all of the fields, and their types. This allows us to take
        advantage of OpenAI's tool/function calling functionality to extract information
        from a prompt according to the context provided by the `BaseModel` schema.

        Args:
            schema: The `BaseModel` schema to extract from the completion.
            prompt: The prompt from which the schema will be extracted.
            retries: The maximum number of times to retry the query on validation error.
            **kwargs: Additional keyword arguments to pass to the API call. You can
                find available keyword arguments here:
                https://platform.openai.com/docs/api-reference/chat/create

        Returns:
            The `Schema` instance extracted from the completion.

        Raises:
            ValidationError: if the schema cannot be instantiated from the completion.
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        tool = convert_base_model_to_tool(schema, OpenAITool)
        completion = await self.create(
            prompt,
            tools=[tool],
            tool_choice={
                "type": "function",
                "function": {"name": tool.__name__},
            },
            extract=True,
            **kwargs,
        )

        try:
            model = schema(**completion.tool.model_dump())  # type: ignore
            model._completion = completion
            return model
        except ValidationError as e:
            if retries > 0:
                logging.info(f"Retrying due to exception: {e}")
                # TODO: update this to include failure history once prompts can handle
                # chat history properly.
                return await self.extract(schema, prompt, retries - 1)
            raise  # re-raise if we have no retries left
