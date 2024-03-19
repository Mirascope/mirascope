"""A module for prompting Mistral API."""
import datetime
from typing import Any, AsyncGenerator, ClassVar, Generator

from mistralai.async_client import MistralAsyncClient
from mistralai.client import MistralClient
from mistralai.constants import ENDPOINT

from ..base import BaseCall
from ..base.types import Message
from ..enums import MessageRole
from .tools import MistralTool
from .types import MistralCallParams, MistralCallResponse, MistralCallResponseChunk


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

    def call(self, **kwargs: Any) -> MistralCallResponse:
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
        start_time = datetime.datetime.now().timestamp() * 1000
        completion = client.chat(messages=self.messages(), **kwargs)
        return MistralCallResponse(
            response=completion,
            tool_types=tool_types,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
        )

    async def call_async(self, **kwargs: Any) -> MistralCallResponse:
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
        start_time = datetime.datetime.now().timestamp() * 1000
        completion = await client.chat(messages=self.messages(), **kwargs)
        return MistralCallResponse(
            response=completion,
            tool_types=tool_types,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
        )

    def stream(self, **kwargs: Any) -> Generator[MistralCallResponseChunk, None, None]:
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
        stream = client.chat_stream(messages=self.messages(), **kwargs)
        for chunk in stream:
            yield MistralCallResponseChunk(chunk=chunk, tool_types=tool_types)

    async def stream_async(
        self, **kwargs: Any
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
        stream = client.chat_stream(messages=self.messages(), **kwargs)
        async for chunk in stream:
            yield MistralCallResponseChunk(chunk=chunk, tool_types=tool_types)
