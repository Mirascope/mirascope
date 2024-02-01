"""Class for interacting with AsyncOpenAI through Chat APIs."""
import logging
from typing import AsyncGenerator, Callable, Optional, Type, TypeVar, Union

from openai import AsyncOpenAI
from pydantic import BaseModel, ValidationError

from ...prompts import Prompt
from ..tools import OpenAITool
from ..types import OpenAIChatCompletion, OpenAIChatCompletionChunk
from ..utils import (
    convert_base_model_to_openai_tool,
    convert_tools_list_to_openai_tools,
    patch_openai_kwargs,
)

logger = logging.getLogger("mirascope")
BaseModelT = TypeVar("BaseModelT", bound=BaseModel)


class AsyncOpenAIChat:
    """A convenience wrapper for the AsyncOpenAI Chat client."""

    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs,
    ):
        """Initializes an instance of `AsyncOpenAIChat."""
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url, **kwargs)
        self.model = model

    async def create(
        self,
        prompt: Optional[Union[Prompt, str]] = None,
        tools: Optional[list[Union[Callable, Type[OpenAITool]]]] = None,
        **kwargs,
    ) -> OpenAIChatCompletion:
        """Asynchronously makes a call to the model using `prompt`.

        Args:
            prompt: The prompt to use for the call. This can either be a `Prompt`
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
        openai_tools = convert_tools_list_to_openai_tools(tools)
        patch_openai_kwargs(kwargs, prompt, openai_tools)

        return OpenAIChatCompletion(
            completion=await self.client.chat.completions.create(
                model=self.model,
                stream=False,
                **kwargs,
            ),
            tool_types=openai_tools if tools else None,
        )

    async def stream(
        self,
        prompt: Optional[Union[Prompt, str]] = None,
        tools: Optional[list[Union[Callable, Type[OpenAITool]]]] = None,
        **kwargs,
    ) -> AsyncGenerator[OpenAIChatCompletionChunk, None]:
        """Asynchronously streams the response for a call to the model using `prompt`.

        Args:
            prompt: The `Prompt` to use for the call.
            tools: A list of `OpenAITool` types or `Callable` functions that the
                creation call can decide to use. If `tools` is provided, `tool_choice`
                will be set to `auto` unless manually specified.
            **kwargs: Additional keyword arguments to pass to the API call. You can
                find available keyword arguments here:
                https://platform.openai.com/docs/api-reference/chat/create

        Yields:
            A `OpenAIChatCompletionChunk` for each chunk of the response.

        Raises:
            ValueError: if neither `prompt` nor `messages` are provided.
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
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
        prompt: Optional[Union[Prompt, str]] = None,
        retries: int = 0,
        **kwargs,
    ) -> BaseModelT:
        """Extracts the given schema from the response of a chat `create` call async.

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
        tool = convert_base_model_to_openai_tool(schema)
        completion = await self.create(
            prompt,
            tools=[tool],
            tool_choice={
                "type": "function",
                "function": {"name": tool.__name__},
            },
            **kwargs,
        )

        try:
            return schema(**completion.tool.model_dump())  # type: ignore
        except ValidationError as e:
            if retries > 0:
                logging.info(f"Retrying due to exception: {e}")
                # TODO: update this to include failure history once prompts can handle
                # chat history properly.
                return await self.extract(schema, prompt, retries - 1)
            raise  # re-raise if we have no retries left
