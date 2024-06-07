"""A module for prompting Mistral API."""

import datetime
from typing import Any, AsyncGenerator, ClassVar, Generator, Union

from mistralai.async_client import MistralAsyncClient
from mistralai.client import MistralClient
from mistralai.constants import ENDPOINT
from tenacity import AsyncRetrying, Retrying

from ..base import BaseCall, retry
from ..base.ops_utils import (
    get_wrapped_async_client,
    get_wrapped_call,
    get_wrapped_client,
)
from ..base.types import Message, UserMessage
from ..enums import MessageRole
from .tools import MistralTool
from .types import MistralCallParams, MistralCallResponse, MistralCallResponseChunk
from .utils import mistral_api_calculate_cost


class MistralCall(
    BaseCall[MistralCallResponse, MistralCallResponseChunk, MistralTool, UserMessage]
):
    """A class for" prompting Mistral's chat API.

    Example:

    ```python
    from mirascope.mistral import MistralCall

    class BookRecommender(MistralCall):
        prompt_template = "Please recommend a {genre} book"

        genre: str

    response = BookRecommender(genre="fantasy").call()
    print(response.content)
    #> There are many great books to read, it ultimately depends...
    ```
    """

    call_params: ClassVar[MistralCallParams] = MistralCallParams()
    _provider: ClassVar[str] = "mistral"

    def messages(self) -> list[Message]:
        """Returns the template as a formatted list of messages."""
        return self._parse_messages(
            [MessageRole.SYSTEM, MessageRole.USER, MessageRole.ASSISTANT]
        )

    @retry
    def call(
        self, retries: Union[int, Retrying] = 0, **kwargs: Any
    ) -> MistralCallResponse:
        """Makes a call to the model using this `MistralCall` instance.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Returns:
            A `MistralCallResponse` instance.

        Raises:
            MistralException: raises any Mistral errors, see:
                https://github.com/mistralai/client-python/blob/main/src/mistralai/exceptions.py
        """
        kwargs, tool_types = self._setup(kwargs, MistralTool)
        client = get_wrapped_client(
            MistralClient(
                api_key=self.api_key,
                endpoint=self.base_url if self.base_url else ENDPOINT,
            ),
            self,
        )
        chat = get_wrapped_call(
            client.chat,
            self,
            response_type=MistralCallResponse,
            tool_types=tool_types,
        )
        messages = self.messages()
        user_message_param = self._get_possible_user_message(messages)
        start_time = datetime.datetime.now().timestamp() * 1000
        completion = chat(messages=messages, **kwargs)
        return MistralCallResponse(
            response=completion,
            user_message_param=user_message_param,
            tool_types=tool_types,
            start_time=start_time,
            cost=mistral_api_calculate_cost(completion.usage, completion.model),
            end_time=datetime.datetime.now().timestamp() * 1000,
        )

    @retry
    async def call_async(
        self, retries: Union[int, AsyncRetrying] = 0, **kwargs: Any
    ) -> MistralCallResponse:
        """Makes an asynchronous call to the model using this `MistralCall` instance.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Returns:
            A `MistralCallResponse` instance.

        Raises:
            MistralException: raises any Mistral errors, see:
                https://github.com/mistralai/client-python/blob/main/src/mistralai/exceptions.py
        """
        kwargs, tool_types = self._setup(kwargs, MistralTool)
        client = get_wrapped_async_client(
            MistralAsyncClient(
                api_key=self.api_key,
                endpoint=self.base_url if self.base_url else ENDPOINT,
            ),
            self,
        )
        chat = get_wrapped_call(
            client.chat,
            self,
            is_async=True,
            response_type=MistralCallResponse,
            tool_types=tool_types,
        )
        messages = self.messages()
        user_message_param = self._get_possible_user_message(messages)
        start_time = datetime.datetime.now().timestamp() * 1000
        completion = await chat(messages=messages, **kwargs)
        return MistralCallResponse(
            response=completion,
            user_message_param=user_message_param,
            tool_types=tool_types,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
            cost=mistral_api_calculate_cost(completion.usage, completion.model),
        )

    @retry
    def stream(
        self, retries: Union[int, Retrying] = 0, **kwargs: Any
    ) -> Generator[MistralCallResponseChunk, None, None]:
        """Streams the response for a call using this `MistralCall` instance.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Returns:
            A `MistralCallResponseChunk` for each chunk of the response.

        Raises:
            MistralException: raises any Mistral errors, see:
                https://github.com/mistralai/client-python/blob/main/src/mistralai/exceptions.py
        """
        kwargs, tool_types = self._setup(kwargs, MistralTool)
        client = get_wrapped_client(
            MistralClient(
                api_key=self.api_key,
                endpoint=self.base_url if self.base_url else ENDPOINT,
            ),
            self,
        )
        chat_stream = get_wrapped_call(
            client.chat_stream,
            self,
            response_chunk_type=MistralCallResponseChunk,
            tool_types=tool_types,
        )
        messages = self.messages()
        user_message_param = self._get_possible_user_message(messages)
        for chunk in chat_stream(messages=messages, **kwargs):
            yield MistralCallResponseChunk(
                chunk=chunk,
                user_message_param=user_message_param,
                tool_types=tool_types,
            )

    @retry
    async def stream_async(
        self, retries: Union[int, AsyncRetrying] = 0, **kwargs: Any
    ) -> AsyncGenerator[MistralCallResponseChunk, None]:
        """Streams the response for an asynchronous call using this `MistralCall`.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Returns:
            A `MistralCallResponseChunk` for each chunk of the response.

        Raises:
            MistralException: raises any Mistral errors, see:
                https://github.com/mistralai/client-python/blob/main/src/mistralai/exceptions.py
        """
        kwargs, tool_types = self._setup(kwargs, MistralTool)
        client = get_wrapped_async_client(
            MistralAsyncClient(
                api_key=self.api_key,
                endpoint=self.base_url if self.base_url else ENDPOINT,
            ),
            self,
        )
        chat_stream = get_wrapped_call(
            client.chat_stream,
            self,
            is_async=True,
            response_chunk_type=MistralCallResponseChunk,
            tool_types=tool_types,
        )
        messages = self.messages()
        user_message_param = self._get_possible_user_message(messages)
        async for chunk in chat_stream(messages=messages, **kwargs):
            yield MistralCallResponseChunk(
                chunk=chunk,
                user_message_param=user_message_param,
                tool_types=tool_types,
            )
