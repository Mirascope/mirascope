"""A module for calling Anthropic's Claude API."""

import datetime
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import Any, AsyncGenerator, ClassVar, Generator, Optional, Type, Union

from anthropic import Anthropic, AsyncAnthropic
from anthropic.types import MessageParam
from tenacity import AsyncRetrying, Retrying

from ..base import BaseCall, retry
from ..base.ops_utils import (
    get_wrapped_async_client,
    get_wrapped_call,
    get_wrapped_client,
)
from ..enums import MessageRole
from .tools import AnthropicTool
from .types import (
    AnthropicCallParams,
    AnthropicCallResponse,
    AnthropicCallResponseChunk,
)
from .utils import anthropic_api_calculate_cost


class AnthropicCall(
    BaseCall[
        AnthropicCallResponse,
        AnthropicCallResponseChunk,
        AnthropicTool,
        MessageParam,
    ]
):
    """A base class for calling Anthropic's Claude models.

    Example:

    ```python
    from mirascope.anthropic import AnthropicCall


    class BookRecommender(AnthropicCall):
        prompt_template = "Please recommend a {genre} book."

        genre: str


    response = BookRecommender(genre="fantasy").call()
    print(response.content)
    #> There are many great books to read, it ultimately depends...
    ```
    """

    call_params: ClassVar[AnthropicCallParams] = AnthropicCallParams()
    _provider: ClassVar[str] = "anthropic"

    def messages(self) -> list[MessageParam]:
        """Returns the template as a formatted list of messages."""
        return self._parse_messages(
            [MessageRole.SYSTEM, MessageRole.USER, MessageRole.ASSISTANT]
        )  # type: ignore

    @retry
    def call(
        self, retries: Union[int, Retrying] = 0, **kwargs: Any
    ) -> AnthropicCallResponse:
        """Makes a call to the model using this `AnthropicCall` instance.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Returns:
            A `AnthropicCallResponse` instance.
        """
        messages, kwargs, tool_types = self._setup_anthropic_kwargs(kwargs)
        user_message_param = self._get_possible_user_message(messages)
        client = get_wrapped_client(
            Anthropic(api_key=self.api_key, base_url=self.base_url), self
        )
        create = get_wrapped_call(
            client.messages.create,
            self,
            response_type=AnthropicCallResponse,
            tool_types=tool_types,
        )
        start_time = datetime.datetime.now().timestamp() * 1000
        message = create(
            messages=messages,
            stream=False,
            **kwargs,
        )
        return AnthropicCallResponse(
            response=message,
            user_message_param=user_message_param,
            tool_types=tool_types,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
            cost=anthropic_api_calculate_cost(message.usage, message.model),
            response_format=self.call_params.response_format,
        )

    @retry
    async def call_async(
        self, retries: Union[int, AsyncRetrying] = 0, **kwargs: Any
    ) -> AnthropicCallResponse:
        """Makes an asynchronous call to the model using this `AnthropicCall` instance.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Returns:
            A `AnthropicCallResponse` instance.
        """
        messages, kwargs, tool_types = self._setup_anthropic_kwargs(kwargs)
        user_message_param = self._get_possible_user_message(messages)
        client = get_wrapped_async_client(
            AsyncAnthropic(api_key=self.api_key, base_url=self.base_url), self
        )
        create = get_wrapped_call(
            client.messages.create,
            self,
            is_async=True,
            response_type=AnthropicCallResponse,
            tool_types=tool_types,
        )
        start_time = datetime.datetime.now().timestamp() * 1000
        message = await create(
            messages=messages,
            stream=False,
            **kwargs,
        )
        return AnthropicCallResponse(
            response=message,
            user_message_param=user_message_param,
            tool_types=tool_types,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
            cost=anthropic_api_calculate_cost(message.usage, message.model),
            response_format=self.call_params.response_format,
        )

    @retry
    def stream(
        self, retries: Union[int, Retrying] = 0, **kwargs: Any
    ) -> Generator[AnthropicCallResponseChunk, None, None]:
        """Streams the response for a call using this `AnthropicCall`.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Yields:
            An `AnthropicCallResponseChunk` for each chunk of the response.
        """
        messages, kwargs, tool_types = self._setup_anthropic_kwargs(kwargs)
        user_message_param = self._get_possible_user_message(messages)
        client = get_wrapped_client(
            Anthropic(api_key=self.api_key, base_url=self.base_url), self
        )
        stream_fn = get_wrapped_call(
            client.messages.stream,
            self,
            response_chunk_type=AnthropicCallResponseChunk,
            tool_types=tool_types,
        )
        stream = stream_fn(messages=messages, **kwargs)
        if isinstance(stream, AbstractContextManager):
            with stream as message_stream:
                for chunk in message_stream:
                    yield AnthropicCallResponseChunk(
                        chunk=chunk,
                        user_message_param=user_message_param,
                        tool_types=tool_types,
                        response_format=self.call_params.response_format,
                    )
        else:
            for chunk in stream:  # type: ignore
                yield AnthropicCallResponseChunk(
                    chunk=chunk,  # type: ignore
                    user_message_param=user_message_param,
                    tool_types=tool_types,
                    response_format=self.call_params.response_format,
                )

    @retry
    async def stream_async(
        self, retries: Union[int, AsyncRetrying] = 0, **kwargs: Any
    ) -> AsyncGenerator[AnthropicCallResponseChunk, None]:
        """Streams the response for an asynchronous call using this `AnthropicCall`.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Yields:
            An `AnthropicCallResponseChunk` for each chunk of the response.
        """
        messages, kwargs, tool_types = self._setup_anthropic_kwargs(kwargs)
        user_message_param = self._get_possible_user_message(messages)
        client = get_wrapped_async_client(
            AsyncAnthropic(api_key=self.api_key, base_url=self.base_url), self
        )
        stream_fn = get_wrapped_call(
            client.messages.stream,
            self,
            is_async=True,
            response_chunk_type=AnthropicCallResponseChunk,
            tool_types=tool_types,
        )
        stream = stream_fn(messages=messages, **kwargs)
        if isinstance(stream, AbstractAsyncContextManager):
            async with stream as message_stream:
                async for chunk in message_stream:  # type: ignore
                    yield AnthropicCallResponseChunk(
                        chunk=chunk,
                        user_message_param=user_message_param,
                        tool_types=tool_types,
                        response_format=self.call_params.response_format,
                    )
        else:
            async for chunk in stream:  # type: ignore
                yield AnthropicCallResponseChunk(
                    chunk=chunk,
                    user_message_param=user_message_param,
                    tool_types=tool_types,
                    response_format=self.call_params.response_format,
                )

    ############################## PRIVATE METHODS ###################################

    def _setup_anthropic_kwargs(
        self,
        kwargs: dict[str, Any],
    ) -> tuple[
        list[MessageParam],
        dict[str, Any],
        Optional[list[Type[AnthropicTool]]],
    ]:
        """Overrides the `BaseCall._setup` for Anthropic specific setup."""
        kwargs, tool_types = self._setup(kwargs, AnthropicTool)
        messages = self.messages()
        system_message = ""
        if "system" in kwargs and kwargs["system"] is not None:
            system_message += f'{kwargs.pop("system")}'
        if messages[0]["role"] == "system":
            if system_message:
                system_message += "\n"
            system_message += messages.pop(0)["content"]
        if self.call_params.response_format == "json":
            if system_message:
                system_message += "\n\n"
            system_message += "Response format: JSON."
            messages.append(
                {
                    "role": "assistant",
                    "content": "Here is the JSON requested with only the fields "
                    "defined in the schema you provided:\n{",
                }
            )
            if "tools" in kwargs:
                tools = kwargs.pop("tools")
                messages[-1]["content"] = (
                    "For each JSON you output, output ONLY the fields defined by these "
                    "schemas. Include a `tool_name` field that EXACTLY MATCHES the "
                    "tool name found in the schema matching this tool:"
                    "\n{schemas}\n{json_msg}".format(
                        schemas="\n\n".join([str(tool) for tool in tools]),
                        json_msg=messages[-1]["content"],
                    )
                )
        if system_message:
            kwargs["system"] = system_message

        return messages, kwargs, tool_types
