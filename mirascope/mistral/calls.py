"""A module for prompting Mistral API."""
import datetime
from typing import Any, AsyncGenerator, ClassVar, Generator, Union

from mistralai.async_client import MistralAsyncClient
from mistralai.client import MistralClient
from mistralai.constants import ENDPOINT
from tenacity import AsyncRetrying, Retrying

from ..base import BaseCall, retry
from ..base.types import Message
from ..enums import MessageRole
from .tools import MistralTool
from .types import MistralCallParams, MistralCallResponse, MistralCallResponseChunk
from .utils import mistral_api_calculate_cost


class MistralCall(BaseCall[MistralCallResponse, MistralCallResponseChunk, MistralTool]):
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
        client = MistralClient(
            api_key=self.api_key,
            endpoint=self.base_url if self.base_url else ENDPOINT,
        )
        chat = client.chat
        if self.call_params.weave:
            chat = self.call_params.weave(chat)  # pragma: no cover
        if self.call_params.logfire:
            chat = self.call_params.logfire(
                chat,
                "mistral",
                response_type=MistralCallResponse,
                tool_types=tool_types,
            )  # pragma: no cover
        start_time = datetime.datetime.now().timestamp() * 1000
        completion = chat(messages=self.messages(), **kwargs)
        return MistralCallResponse(
            response=completion,
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
        client = MistralAsyncClient(
            api_key=self.api_key,
            endpoint=self.base_url if self.base_url else ENDPOINT,
        )
        chat = client.chat
        if self.call_params.weave:
            chat = self.call_params.weave(chat)  # pragma: no cover
        elif self.call_params.logfire_async:
            chat = self.call_params.logfire_async(
                chat,
                "mistral",
                response_type=MistralCallResponse,
                tool_types=tool_types,
            )  # pragma: no cover

        start_time = datetime.datetime.now().timestamp() * 1000
        completion = await chat(messages=self.messages(), **kwargs)
        return MistralCallResponse(
            response=completion,
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
        client = MistralClient(
            api_key=self.api_key,
            endpoint=self.base_url if self.base_url else ENDPOINT,
        )
        chat_stream = client.chat_stream
        if self.call_params.logfire:
            chat_stream = self.call_params.logfire(
                chat_stream, "mistral", response_chunk_type=MistralCallResponseChunk
            )  # pragma: no cover
        stream = chat_stream(messages=self.messages(), **kwargs)

        for chunk in stream:
            yield MistralCallResponseChunk(chunk=chunk, tool_types=tool_types)

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
        client = MistralAsyncClient(
            api_key=self.api_key,
            endpoint=self.base_url if self.base_url else ENDPOINT,
        )
        chat_stream = client.chat_stream
        if self.call_params.logfire_async:
            chat_stream = self.call_params.logfire_async(
                chat_stream, "mistral", response_chunk_type=MistralCallResponseChunk
            )  # pragma: no cover
        stream = chat_stream(messages=self.messages(), **kwargs)
        async for chunk in stream:
            yield MistralCallResponseChunk(chunk=chunk, tool_types=tool_types)
