"""A module for calling Groq's Cloud API."""

import datetime
import inspect
import json
from typing import Any, AsyncGenerator, ClassVar, Generator, Optional, Type, Union

from groq import AsyncGroq, Groq
from groq.types.chat import ChatCompletionMessageParam, ChatCompletionUserMessageParam
from groq.types.chat.completion_create_params import ResponseFormat
from tenacity import AsyncRetrying, Retrying

from ..base import BaseCall, retry
from ..base.ops_utils import (
    get_wrapped_async_client,
    get_wrapped_call,
    get_wrapped_client,
)
from ..enums import MessageRole
from .tools import GroqTool
from .types import GroqCallParams, GroqCallResponse, GroqCallResponseChunk
from .utils import groq_api_calculate_cost

JSON_MODE_CONTENT = """
Extract a valid JSON object instance from to content using the following schema:

{schema}
""".strip()


def _json_mode_content(tool_type: Type[GroqTool]) -> str:
    """Returns the formatted `JSON_MODE_CONTENT` with the given tool type."""
    return JSON_MODE_CONTENT.format(
        schema=json.dumps(tool_type.model_json_schema(), indent=2)
    )


class GroqCall(
    BaseCall[
        GroqCallResponse,
        GroqCallResponseChunk,
        GroqTool,
        ChatCompletionUserMessageParam,
    ]
):
    """A base class for calling Groq's Cloud API.

    Example:

    ```python
    from mirascope.groq import GroqCall


    class BookRecommender(GroqCall):
        prompt_template = "Please recommend a {genre} book"

        genre: str

    response = BookRecommender(genre="fantasy").call()
    print(response.content)
    #> There are many great books to read, it ultimately depends...
    ```
    """

    call_params: ClassVar[GroqCallParams] = GroqCallParams()
    _provider: ClassVar[str] = "groq"

    def messages(self) -> list[ChatCompletionMessageParam]:
        """Returns the template as a formatted list of messages."""
        return self._parse_messages(
            [MessageRole.SYSTEM, MessageRole.USER, MessageRole.ASSISTANT]
        )  # type: ignore

    @retry
    def call(
        self, retries: Union[int, Retrying] = 0, **kwargs: Any
    ) -> GroqCallResponse:
        """Makes a call to the model using this `GroqCall` instance.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Returns:
            A `GroqCallResponse` instance.
        """
        kwargs, tool_types = self._setup_groq_kwargs(kwargs)
        client = get_wrapped_client(
            Groq(api_key=self.api_key, base_url=self.base_url), self
        )
        create = get_wrapped_call(
            client.chat.completions.create,
            self,
            response_type=GroqCallResponse,
            tool_types=tool_types,
        )
        messages = self._update_messages_if_json(self.messages(), tool_types)
        user_message_param = self._get_possible_user_message(messages)
        start_time = datetime.datetime.now().timestamp() * 1000
        completion = create(messages=messages, stream=False, **kwargs)
        return GroqCallResponse(
            response=completion,
            user_message_param=user_message_param,
            tool_types=tool_types,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
            response_format=self.call_params.response_format,
            cost=groq_api_calculate_cost(completion.usage, completion.model),
        )

    @retry
    async def call_async(
        self, retries: Union[int, AsyncRetrying] = 0, **kwargs: Any
    ) -> GroqCallResponse:
        """Makes an asynchronous call to the model using this `GroqCall`.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Returns:
            An `GroqCallResponse` instance.
        """
        kwargs, tool_types = self._setup_groq_kwargs(kwargs)
        client = get_wrapped_async_client(
            AsyncGroq(api_key=self.api_key, base_url=self.base_url), self
        )
        create = get_wrapped_call(
            client.chat.completions.create,
            self,
            is_async=True,
            response_type=GroqCallResponse,
            tool_types=tool_types,
        )
        messages = self._update_messages_if_json(self.messages(), tool_types)
        user_message_param = self._get_possible_user_message(messages)
        start_time = datetime.datetime.now().timestamp() * 1000
        completion = await create(messages=messages, stream=False, **kwargs)
        return GroqCallResponse(
            response=completion,
            user_message_param=user_message_param,
            tool_types=tool_types,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
            response_format=self.call_params.response_format,
            cost=groq_api_calculate_cost(completion.usage, completion.model),
        )

    @retry
    def stream(
        self, retries: Union[int, Retrying] = 0, **kwargs: Any
    ) -> Generator[GroqCallResponseChunk, None, None]:
        """Streams the response for a call using this `GroqCall`.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Yields:
            A `GroqCallResponseChunk` for each chunk of the response.
        """
        kwargs, tool_types = self._setup_groq_kwargs(kwargs)
        client = get_wrapped_client(
            Groq(api_key=self.api_key, base_url=self.base_url), self
        )
        messages = self._update_messages_if_json(self.messages(), tool_types)
        user_message_param = self._get_possible_user_message(messages)
        create = get_wrapped_call(
            client.chat.completions.create,
            self,
            response_chunk_type=GroqCallResponseChunk,
            tool_types=tool_types,
        )
        stream = create(messages=messages, stream=True, **kwargs)
        for completion in stream:
            yield GroqCallResponseChunk(
                chunk=completion,
                user_message_param=user_message_param,
                tool_types=tool_types,
                response_format=self.call_params.response_format,
            )

    @retry
    async def stream_async(
        self, retries: Union[int, AsyncRetrying] = 0, **kwargs: Any
    ) -> AsyncGenerator[GroqCallResponseChunk, None]:
        """Streams the response for an asynchronous call using this `GroqCall`.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Yields:
            A `GroqCallResponseChunk` for each chunk of the response.
        """
        kwargs, tool_types = self._setup_groq_kwargs(kwargs)
        client = get_wrapped_async_client(
            AsyncGroq(api_key=self.api_key, base_url=self.base_url), self
        )
        messages = self._update_messages_if_json(self.messages(), tool_types)
        user_message_param = self._get_possible_user_message(messages)
        create = get_wrapped_call(
            client.chat.completions.create,
            self,
            is_async=True,
            response_chunk_type=GroqCallResponseChunk,
            tool_types=tool_types,
        )
        stream = create(messages=messages, stream=True, **kwargs)
        if inspect.iscoroutine(stream):
            stream = await stream
        async for completion in stream:  # type: ignore
            yield GroqCallResponseChunk(
                chunk=completion,
                user_message_param=user_message_param,
                tool_types=tool_types,
                response_format=self.call_params.response_format,
            )

    ############################## PRIVATE METHODS ###################################

    def _setup_groq_kwargs(
        self,
        kwargs: dict[str, Any],
    ) -> tuple[
        dict[str, Any],
        Optional[list[Type[GroqTool]]],
    ]:
        """Overrides the `BaseCall._setup` for Groq specific setup."""
        kwargs, tool_types = self._setup(kwargs, GroqTool)
        if (
            self.call_params.response_format == ResponseFormat(type="json_object")
            and tool_types
        ):
            kwargs.pop("tools")
        return kwargs, tool_types

    def _update_messages_if_json(
        self,
        messages: list[ChatCompletionMessageParam],
        tool_types: Optional[list[type[GroqTool]]],
    ) -> list[ChatCompletionMessageParam]:
        if (
            self.call_params.response_format == ResponseFormat(type="json_object")
            and tool_types
        ):
            messages.append(
                ChatCompletionUserMessageParam(
                    role="user",
                    content=_json_mode_content(tool_type=tool_types[0]),
                )
            )
        return messages
