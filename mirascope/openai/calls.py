"""A module for calling OpenAI's Chat Completion models."""
import datetime
import json
from typing import Any, AsyncGenerator, ClassVar, Generator, Optional, Type

from openai import AsyncOpenAI, OpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.completion_create_params import ResponseFormat

from ..base import BaseCall
from ..enums import MessageRole
from .tools import OpenAITool
from .types import OpenAICallParams, OpenAICallResponse, OpenAICallResponseChunk

JSON_MODE_CONTENT = """
Extract a valid JSON object instance from to content using the following schema:

{schema}
""".strip()


def _json_mode_content(tool_type: Type[OpenAITool]) -> str:
    """Returns the formatted `JSON_MODE_CONTENT` with the given tool type."""
    return JSON_MODE_CONTENT.format(
        schema=json.dumps(tool_type.model_json_schema(), indent=2)
    )


class OpenAICall(BaseCall[OpenAICallResponse, OpenAICallResponseChunk, OpenAITool]):
    """A base class for calling OpenAI's Chat Completion models.

    Example:

    ```python
    from mirascope.openai import OpenAICall


    class BookRecommender(OpenAICall):
        prompt_template = "Please recommend a {genre} book"

        genre: str

    response = BookRecommender(genre="fantasy").call()
    print(response.content)
    #> There are many great books to read, it ultimately depends...
    ```
    """

    call_params: ClassVar[OpenAICallParams] = OpenAICallParams()

    def messages(self) -> list[ChatCompletionMessageParam]:
        """Returns the template as a formatted list of messages."""
        message_type_by_role = {
            MessageRole.SYSTEM: ChatCompletionSystemMessageParam,
            MessageRole.USER: ChatCompletionUserMessageParam,
            MessageRole.ASSISTANT: ChatCompletionAssistantMessageParam,
            MessageRole.TOOL: ChatCompletionToolMessageParam,
        }
        return [
            message_type_by_role[MessageRole(message["role"])](
                role=message["role"], content=message["content"]
            )
            for message in self._parse_messages(list(message_type_by_role.keys()))
        ]

    def call(self, **kwargs: Any) -> OpenAICallResponse:
        """Makes a call to the model using this `OpenAICall` instance.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Returns:
            A `OpenAICallResponse` instance.

        Raises:
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        kwargs, tool_types = self._setup_openai_kwargs(kwargs)
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        if self.call_params.wrapper is not None:
            client = self.call_params.wrapper(client)
        messages = self._update_messages_if_json(self.messages(), tool_types)
        start_time = datetime.datetime.now().timestamp() * 1000
        completion = client.chat.completions.create(
            messages=messages,
            stream=False,
            **kwargs,
        )
        openai_call_response = OpenAICallResponse(
            response=completion,
            tool_types=tool_types,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
        )
        openai_call_response.response_format = self.call_params.response_format
        return openai_call_response

    async def call_async(self, **kwargs: Any) -> OpenAICallResponse:
        """Makes an asynchronous call to the model using this `OpenAICall`.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Returns:
            An `OpenAICallResponse` instance.

        Raises:
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        kwargs, tool_types = self._setup(kwargs, OpenAITool)
        client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        if self.call_params.wrapper_async is not None:
            client = self.call_params.wrapper_async(client)
        messages = self._update_messages_if_json(self.messages(), tool_types)
        start_time = datetime.datetime.now().timestamp() * 1000
        completion = await client.chat.completions.create(
            messages=messages,
            stream=False,
            **kwargs,
        )
        openai_call_response = OpenAICallResponse(
            response=completion,
            tool_types=tool_types,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
        )
        openai_call_response.response_format = self.call_params.response_format
        return openai_call_response

    def stream(self, **kwargs: Any) -> Generator[OpenAICallResponseChunk, None, None]:
        """Streams the response for a call using this `OpenAICall`.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Yields:
            A `OpenAICallResponseChunk` for each chunk of the response.

        Raises:
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        kwargs, tool_types = self._setup(kwargs, OpenAITool)
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        if self.call_params.wrapper is not None:
            client = self.call_params.wrapper(client)
        messages = self._update_messages_if_json(self.messages(), tool_types)
        stream = client.chat.completions.create(
            messages=messages,
            stream=True,
            **kwargs,
        )
        for chunk in stream:
            openai_call_response_chunk = OpenAICallResponseChunk(
                chunk=chunk, tool_types=tool_types
            )
            openai_call_response_chunk.response_format = (
                self.call_params.response_format
            )
            yield openai_call_response_chunk

    async def stream_async(
        self, **kwargs: Any
    ) -> AsyncGenerator[OpenAICallResponseChunk, None]:
        """Streams the response for an asynchronous call using this `OpenAICall`.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Yields:
            A `OpenAICallResponseChunk` for each chunk of the response.

        Raises:
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        kwargs, tool_types = self._setup(kwargs, OpenAITool)
        client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        if self.call_params.wrapper_async is not None:
            client = self.call_params.wrapper_async(client)
        messages = self._update_messages_if_json(self.messages(), tool_types)
        stream = await client.chat.completions.create(
            messages=messages,
            stream=True,
            **kwargs,
        )
        async for chunk in stream:
            openai_call_response_chunk = OpenAICallResponseChunk(
                chunk=chunk, tool_types=tool_types
            )
            openai_call_response_chunk.response_format = (
                self.call_params.response_format
            )
            yield openai_call_response_chunk

    ############################## PRIVATE METHODS ###################################

    def _setup_openai_kwargs(
        self,
        kwargs: dict[str, Any],
    ) -> tuple[
        dict[str, Any],
        Optional[list[Type[OpenAITool]]],
    ]:
        """Overrides the `BaseCall._setup` for Anthropic specific setup."""
        kwargs, tool_types = self._setup(kwargs, OpenAITool)
        if (
            self.call_params.response_format == ResponseFormat(type="json_object")
            and tool_types
        ):
            kwargs.pop("tools")
        return kwargs, tool_types

    def _update_messages_if_json(
        self,
        messages: list[ChatCompletionMessageParam],
        tool_types: Optional[list[type[OpenAITool]]],
    ) -> list[ChatCompletionMessageParam]:
        if (
            self.call_params.response_format == ResponseFormat(type="json_object")
            and tool_types
        ):
            messages.append(
                ChatCompletionUserMessageParam(
                    role="user", content=_json_mode_content(tool_type=tool_types[0])
                )
            )
        return messages
