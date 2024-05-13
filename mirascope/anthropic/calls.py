"""A module for calling Anthropic's Claude API."""
import datetime
from typing import Any, AsyncGenerator, ClassVar, Generator, Optional, Type, Union

from anthropic import Anthropic, AsyncAnthropic
from anthropic.types import MessageParam
from tenacity import AsyncRetrying, Retrying

from ..base import BaseCall, retry
from ..enums import MessageRole
from .tools import AnthropicTool
from .types import (
    AnthropicCallParams,
    AnthropicCallResponse,
    AnthropicCallResponseChunk,
)
from .utils import anthropic_api_calculate_cost


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
        client = Anthropic(api_key=self.api_key, base_url=self.base_url)
        if self.call_params.wrapper is not None:
            client = self.call_params.wrapper(client)

        create = client.messages.create
        if tool_types:
            create = client.beta.tools.messages.create  # type: ignore
        if self.call_params.weave is not None:
            create = self.call_params.weave(create)  # pragma: no cover
        if self.call_params.logfire:
            create = self.call_params.logfire(
                create,
                "anthropic",
                response_type=AnthropicCallResponse,
                tool_types=tool_types,
            )  # pragma: no cover
        if self.call_params.langfuse:
            create = self.call_params.langfuse(
                create, "anthropic", response_type=AnthropicCallResponse
            )  # pragma: no cover
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
        client = AsyncAnthropic(api_key=self.api_key, base_url=self.base_url)
        if self.call_params.wrapper_async is not None:
            client = self.call_params.wrapper_async(client)
        create = client.messages.create
        if tool_types:
            create = client.beta.tools.messages.create  # type: ignore
        if self.call_params.weave is not None:
            create = self.call_params.weave(create)  # pragma: no cover
        if self.call_params.logfire_async:
            create = self.call_params.logfire_async(
                create,
                "anthropic",
                response_type=AnthropicCallResponse,
                tool_types=tool_types,
            )  # pragma: no cover
        if self.call_params.langfuse:
            create = self.call_params.langfuse(
                create, "anthropic", is_async=True, response_type=AnthropicCallResponse
            )  # pragma: no cover
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
        client = Anthropic(api_key=self.api_key, base_url=self.base_url)
        if self.call_params.wrapper is not None:
            client = self.call_params.wrapper(client)
        if self.call_params.logfire or self.call_params.langfuse:  # pragma: no cover
            stream = client.messages.stream
            if self.call_params.logfire:
                stream = self.call_params.logfire(
                    stream,
                    "anthropic",
                    response_chunk_type=AnthropicCallResponseChunk,
                )
            if self.call_params.langfuse:
                stream = self.call_params.langfuse(
                    stream,
                    "anthropic",
                    response_chunk_type=AnthropicCallResponseChunk,
                )
            for chunk in stream(messages=messages, **kwargs):  # type: ignore
                yield AnthropicCallResponseChunk(
                    chunk=chunk,
                    tool_types=tool_types,
                    response_format=self.call_params.response_format,
                )
        else:
            stream = client.messages.stream
            with stream(messages=messages, **kwargs) as message_stream:
                for chunk in message_stream:
                    yield AnthropicCallResponseChunk(
                        chunk=chunk,
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
        client = AsyncAnthropic(api_key=self.api_key, base_url=self.base_url)
        if self.call_params.wrapper_async is not None:
            client = self.call_params.wrapper_async(client)
        if (
            self.call_params.logfire_async or self.call_params.langfuse
        ):  # pragma: no cover
            stream = client.messages.stream
            if self.call_params.logfire_async:
                stream = self.call_params.logfire_async(
                    stream,
                    "anthropic",
                    response_chunk_type=AnthropicCallResponseChunk,
                )
            if self.call_params.langfuse:
                stream = self.call_params.langfuse(
                    stream,
                    "anthropic",
                    is_async=True,
                    response_chunk_type=AnthropicCallResponseChunk,
                )
            async for chunk in stream(messages=messages, **kwargs):  # type: ignore
                yield AnthropicCallResponseChunk(
                    chunk=chunk,
                    tool_types=tool_types,
                    response_format=self.call_params.response_format,
                )
        else:
            async with client.messages.stream(
                messages=messages, **kwargs
            ) as message_stream:
                async for chunk in message_stream:  # type: ignore
                    yield AnthropicCallResponseChunk(
                        chunk=chunk,
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
