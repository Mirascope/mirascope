"""A module for calling Cohere's chat models."""

import datetime
from typing import Any, AsyncGenerator, ClassVar, Generator, Optional, Type, Union

from cohere import AsyncClient, Client
from cohere.types import ChatMessage
from tenacity import AsyncRetrying, Retrying

from ..base import BaseCall, retry
from ..base.ops_utils import (
    get_wrapped_async_client,
    get_wrapped_call,
    get_wrapped_client,
)
from ..enums import MessageRole
from .tools import CohereTool
from .types import CohereCallParams, CohereCallResponse, CohereCallResponseChunk
from .utils import cohere_api_calculate_cost


class CohereCall(
    BaseCall[CohereCallResponse, CohereCallResponseChunk, CohereTool, ChatMessage]
):
    """A base class for calling Cohere's chat models.

    Example:

    ```python
    from mirascope.cohere import CohereCall


    class BookRecommender(CohereCall):
        prompt_template = "Please recommend a {genre} book"

        genre: str

    response = BookRecommender(genre="fantasy").call()
    print(response.content)
    #> There are many great books to read, it ultimately depends...
    ```
    """

    call_params: ClassVar[CohereCallParams] = CohereCallParams()
    _provider: ClassVar[str] = "cohere"

    def messages(self) -> list[ChatMessage]:
        """Returns the template as a formatted list of messages."""
        return [
            ChatMessage(role=message["role"].upper(), message=message["content"])  # type: ignore
            for message in self._parse_messages(
                [MessageRole.SYSTEM, MessageRole.USER, MessageRole.CHATBOT]
            )
        ]

    @retry
    def call(
        self, retries: Union[int, Retrying] = 0, **kwargs: Any
    ) -> CohereCallResponse:
        """Makes a call to the model using this `CohereCall` instance.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Returns:
            A `CohereCallResponse` instance.
        """
        message, kwargs, tool_types = self._setup_cohere_kwargs(kwargs)
        co = get_wrapped_client(
            Client(api_key=self.api_key, base_url=self.base_url), self
        )

        chat = get_wrapped_call(
            co.chat, self, response_type=CohereCallResponse, tool_types=tool_types
        )
        start_time = datetime.datetime.now().timestamp() * 1000
        response = chat(message=message, **kwargs)
        cost = None
        if response.meta and response.meta.billed_units:
            cost = cohere_api_calculate_cost(
                response.meta.billed_units, self.call_params.model
            )
        return CohereCallResponse(
            response=response,
            user_message_param=ChatMessage(message=message, role="user"),  # type: ignore
            tool_types=tool_types,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
            cost=cost,
        )

    @retry
    async def call_async(
        self, retries: Union[int, AsyncRetrying] = 0, **kwargs: Any
    ) -> CohereCallResponse:
        """Makes an asynchronous call to the model using this `CohereCall`.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Returns:
            An `CohereCallResponse` instance.
        """
        message, kwargs, tool_types = self._setup_cohere_kwargs(kwargs)
        co = get_wrapped_async_client(
            AsyncClient(api_key=self.api_key, base_url=self.base_url), self
        )
        chat = get_wrapped_call(
            co.chat,
            self,
            is_async=True,
            response_type=CohereCallResponse,
            tool_types=tool_types,
        )
        start_time = datetime.datetime.now().timestamp() * 1000
        response = await chat(message=message, **kwargs)
        cost = None
        if response.meta and response.meta.billed_units:
            cost = cohere_api_calculate_cost(
                response.meta.billed_units, self.call_params.model
            )
        return CohereCallResponse(
            response=response,
            user_message_param=ChatMessage(message=message, role="user"),  # type: ignore
            tool_types=tool_types,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
            cost=cost,
        )

    @retry
    def stream(
        self, retries: Union[int, Retrying] = 0, **kwargs: Any
    ) -> Generator[CohereCallResponseChunk, None, None]:
        """Streams the response for a call using this `CohereCall`.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Yields:
            A `CohereCallResponseChunk` for each chunk of the response.
        """
        message, kwargs, tool_types = self._setup_cohere_kwargs(kwargs)
        co = get_wrapped_client(
            Client(api_key=self.api_key, base_url=self.base_url), self
        )
        chat_stream = get_wrapped_call(
            co.chat_stream,
            self,
            response_chunk_type=CohereCallResponseChunk,
            tool_types=tool_types,
        )
        user_message_param = ChatMessage(message=message, role="user")  # type: ignore
        for event in chat_stream(message=message, **kwargs):
            yield CohereCallResponseChunk(
                chunk=event,
                user_message_param=user_message_param,
                tool_types=tool_types,
            )

    @retry
    async def stream_async(
        self, retries: Union[int, AsyncRetrying] = 0, **kwargs: Any
    ) -> AsyncGenerator[CohereCallResponseChunk, None]:
        """Streams the response for an asynchronous call using this `CohereCall`.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Yields:
            A `CohereCallResponseChunk` for each chunk of the response.
        """
        message, kwargs, tool_types = self._setup_cohere_kwargs(kwargs)
        co = get_wrapped_async_client(
            AsyncClient(api_key=self.api_key, base_url=self.base_url), self
        )
        chat_stream = get_wrapped_call(
            co.chat_stream,
            self,
            is_async=True,
            response_chunk_type=CohereCallResponseChunk,
            tool_types=tool_types,
        )
        user_message_param = ChatMessage(message=message, role="user")  # type: ignore
        async for event in chat_stream(message=message, **kwargs):
            yield CohereCallResponseChunk(
                chunk=event,
                user_message_param=user_message_param,
                tool_types=tool_types,
            )

    ############################## PRIVATE METHODS ###################################

    def _setup_cohere_kwargs(
        self, kwargs: dict[str, Any]
    ) -> tuple[str, dict[str, Any], Optional[list[Type[CohereTool]]]]:
        """Overrides the `BaseCall._setup` for Cohere specific setup."""
        kwargs, tool_types = self._setup(kwargs, CohereTool)
        messages = self.messages()
        preamble = ""
        if "preamble" in kwargs and kwargs["preamble"] is not None:
            preamble += kwargs.pop("preamble")
        if messages[0].role == "SYSTEM":  # type: ignore
            preamble += messages.pop(0).message
        if preamble:
            kwargs["preamble"] = preamble
        if len(messages) > 1:
            kwargs["chat_history"] = messages[:-1]
        if hasattr(self, "documents"):
            kwargs["documents"] = self.documents
        return messages[-1].message, kwargs, tool_types
