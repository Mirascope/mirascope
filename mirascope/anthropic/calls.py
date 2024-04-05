"""A module for calling Anthropic's Claude API."""
import datetime
from typing import Any, AsyncGenerator, ClassVar, Generator, Optional, Type

from anthropic import Anthropic, AsyncAnthropic
from anthropic.types import MessageParam

from ..base import BaseCall
from ..enums import MessageRole
from .tools import AnthropicTool
from .types import (
    AnthropicCallParams,
    AnthropicCallResponse,
    AnthropicCallResponseChunk,
)


class AnthropicCall(
    BaseCall[AnthropicCallResponse, AnthropicCallResponseChunk, AnthropicTool]
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

    def messages(self) -> list[MessageParam]:
        """Returns the template as a formatted list of messages."""
        return self._parse_messages(
            [MessageRole.SYSTEM, MessageRole.USER, MessageRole.ASSISTANT]
        )  # type: ignore

    def call(self, **kwargs: Any) -> AnthropicCallResponse:
        """Makes a call to the model using this `AnthropicCall` instance.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Returns:
            A `AnthropicCallResponse` instance.
        """
        messages, kwargs, tool_types = self._setup_anthropic_kwargs(kwargs)
        client = Anthropic(api_key=self.api_key, base_url=self.base_url)
        if self.call_params.wrapper is not None:
            client = self.call_params.wrapper(client)
        create = client.messages.create
        if tool_types:
            create = client.beta.tools.messages.create  # type: ignore
        if self.call_params.weave is not None:
            create = self.call_params.weave(create)  # pragma: no cover
        start_time = datetime.datetime.now().timestamp() * 1000
        message = create(
            messages=messages,
            stream=False,
            **kwargs,
        )
        return AnthropicCallResponse(
            response=message,
            tool_types=tool_types,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
        )

    async def call_async(self, **kwargs: Any) -> AnthropicCallResponse:
        """Makes an asynchronous call to the model using this `AnthropicCall` instance.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Returns:
            A `AnthropicCallResponse` instance.
        """
        messages, kwargs, tool_types = self._setup_anthropic_kwargs(kwargs)
        client = AsyncAnthropic(api_key=self.api_key, base_url=self.base_url)
        if self.call_params.wrapper_async is not None:
            client = self.call_params.wrapper_async(client)
        create = client.messages.create
        if tool_types:
            create = client.beta.tools.messages.create  # type: ignore
        if self.call_params.weave is not None:
            create = self.call_params.weave(create)  # pragma: no cover
        start_time = datetime.datetime.now().timestamp() * 1000
        message = await create(
            messages=messages,
            stream=False,
            **kwargs,
        )
        return AnthropicCallResponse(
            response=message,
            tool_types=tool_types,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
        )

    def stream(
        self, **kwargs: Any
    ) -> Generator[AnthropicCallResponseChunk, None, None]:
        """Streams the response for a call using this `AnthropicCall`.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Yields:
            An `AnthropicCallResponseChunk` for each chunk of the response.
        """
        messages, kwargs, tool_types = self._setup_anthropic_kwargs(kwargs)
        client = Anthropic(api_key=self.api_key, base_url=self.base_url)
        if self.call_params.wrapper is not None:
            client = self.call_params.wrapper(client)
        with client.messages.stream(messages=messages, **kwargs) as stream:
            for chunk in stream:
                yield AnthropicCallResponseChunk(chunk=chunk, tool_types=tool_types)

    async def stream_async(
        self, **kwargs: Any
    ) -> AsyncGenerator[AnthropicCallResponseChunk, None]:
        """Streams the response for an asynchronous call using this `AnthropicCall`.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Yields:
            An `AnthropicCallResponseChunk` for each chunk of the response.
        """
        messages, kwargs, tool_types = self._setup_anthropic_kwargs(kwargs)
        client = AsyncAnthropic(api_key=self.api_key, base_url=self.base_url)
        if self.call_params.wrapper_async is not None:
            client = self.call_params.wrapper_async(client)
        async with client.messages.stream(messages=messages, **kwargs) as stream:
            async for chunk in stream:
                yield AnthropicCallResponseChunk(chunk=chunk, tool_types=tool_types)

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
            system_message += kwargs.pop("system")
        if messages[0]["role"] == "system":
            system_message += messages.pop(0)["content"]
        if system_message:
            kwargs["system"] = system_message
        return messages, kwargs, tool_types
