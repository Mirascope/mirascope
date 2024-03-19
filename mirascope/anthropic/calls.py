"""A module for calling Anthropic's Claude API."""
import datetime
from textwrap import dedent
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


class AnthropicCall(BaseCall[AnthropicCallResponse, AnthropicCallResponseChunk, Any]):
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
        start_time = datetime.datetime.now().timestamp() * 1000
        message = client.messages.create(
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
        start_time = datetime.datetime.now().timestamp() * 1000
        message = await client.messages.create(
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
        if messages[0]["role"] == "system":
            system_message += messages.pop(0)["content"]
        if tool_types:
            tool_schemas = kwargs.pop("tools")
            system_message += self._write_tools_system_message(tool_schemas)
            kwargs["stop_sequences"] = ["</function_calls>"]
        if system_message:
            kwargs["system"] = system_message
        return messages, kwargs, tool_types

    def _write_tools_system_message(self, tool_schemas: list[str]) -> str:
        """Returns the Anthropic Tools System Message from their guide."""
        return dedent(
            """
        In this environment you have access to a set of tools you can use to answer the user's question.

        You may call them like this:
        <function_calls>
        <invoke>
        <tool_name>$TOOL_NAME</tool_name>
        <parameters>
        <$PARAMETER_NAME>$PARAMETER_VALUE</$PARAMETER_NAME>
        ...
        </parameters>
        </invoke>
        ...
        </function_calls>

        Make sure to include all parameters in the tool schema when requested.
        If you want to call multiple tools, you should put all of the tools inside of the <function_calls> tag as multiple <invoke> elements.

        To output nested structured data, encode it as valid XML with tags and values. For example:

        List[int]:
        <parameterName>
            <item>1</item>
            <item>2</item>
            <item>3</item>
        </parameterName>

        List[object]:
        <parameterName>
            <item>
                <objectName>
                    <objectValue>value</objectValue>
                </objectName>
            </item>
        </parameterName>

        Dictionary:
        <parameterName>
            <entry>
                <key>key1</key>
                <value>value1</value>
            </entry>
            <entry>
                <key>key2</key>
                <value>value2</value>
            </entry>
        </parameterName>

        Remember, the above are just examples.
        Make sure to properly nest by wrapping elements in lists with the <item> tag and dictionary elements with <entry> as necessary.
        DO NOT FORGET THESE TAGS. Without these tags, we cannot properly parse the information you send.

        Here are the tools available:
        <tools>
        {tool_schemas}
        </tools>
            """.format(tool_schemas=tool_schemas)
        )
