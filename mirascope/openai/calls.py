"""A module for calling OpenAI's Chat Completion models."""

import datetime
import json
from typing import (
    Any,
    AsyncGenerator,
    ClassVar,
    Generator,
    Optional,
    Type,
    Union,
    overload,
)

from openai import AsyncAzureOpenAI, AsyncOpenAI, AzureOpenAI, OpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.completion_create_params import ResponseFormat
from tenacity import AsyncRetrying, Retrying

from mirascope.base.ops_utils import (
    get_wrapped_async_client,
    get_wrapped_call,
    get_wrapped_client,
)

from ..base import BaseCall
from ..base.utils import retry
from ..enums import MessageRole
from .tools import OpenAITool
from .types import OpenAICallParams, OpenAICallResponse, OpenAICallResponseChunk
from .utils import openai_api_calculate_cost

JSON_MODE_CONTENT = """
Extract a valid JSON object instance from to content using the following schema:

{schema}
""".strip()


def _json_mode_content(tool_type: Type[OpenAITool]) -> str:
    """Returns the formatted `JSON_MODE_CONTENT` with the given tool type."""
    return JSON_MODE_CONTENT.format(
        schema=json.dumps(tool_type.model_json_schema(), indent=2)
    )


class OpenAICall(
    BaseCall[
        OpenAICallResponse,
        OpenAICallResponseChunk,
        OpenAITool,
        ChatCompletionUserMessageParam,
    ]
):
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
    _provider: ClassVar[str] = "openai"

    def messages(self) -> list[ChatCompletionMessageParam]:
        """Returns the template as a formatted list of messages."""
        message_type_by_role = {
            MessageRole.SYSTEM: ChatCompletionSystemMessageParam,
            MessageRole.USER: ChatCompletionUserMessageParam,
            MessageRole.ASSISTANT: ChatCompletionAssistantMessageParam,
            MessageRole.TOOL: ChatCompletionToolMessageParam,
        }
        return [
            message_type_by_role[MessageRole(message["role"])](**message)
            for message in self._parse_messages(list(message_type_by_role.keys()))
        ]

    @retry
    def call(
        self, retries: Union[int, Retrying] = 0, **kwargs: Any
    ) -> OpenAICallResponse:
        """Makes a call to the model using this `OpenAICall` instance.

        Args:
            retries: An integer for the number of times to retry the call or
                a `tenacity.Retrying` instance.
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Returns:
            A `OpenAICallResponse` instance.

        Raises:
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        kwargs, tool_types = self._setup_openai_kwargs(kwargs)
        client = self._setup_openai_client(OpenAI)
        create = get_wrapped_call(
            client.chat.completions.create,
            self,
            response_type=OpenAICallResponse,
            tool_types=tool_types,
        )
        messages = self._update_messages_if_json(self.messages(), tool_types)
        user_message_param = self._get_possible_user_message(messages)
        start_time = datetime.datetime.now().timestamp() * 1000
        completion = create(
            messages=messages,
            stream=False,
            **kwargs,
        )
        return OpenAICallResponse(
            response=completion,
            user_message_param=user_message_param,
            tool_types=tool_types,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
            cost=openai_api_calculate_cost(completion.usage, completion.model),
            response_format=self.call_params.response_format,
        )

    @retry
    async def call_async(
        self, retries: Union[int, AsyncRetrying] = 0, **kwargs: Any
    ) -> OpenAICallResponse:
        """Makes an asynchronous call to the model using this `OpenAICall`.

        Args:
            retries: An integer for the number of times to retry the call or
                a `tenacity.AsyncRetrying` instance.
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Returns:
            An `OpenAICallResponse` instance.

        Raises:
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        kwargs, tool_types = self._setup_openai_kwargs(kwargs)
        client = self._setup_openai_client(AsyncOpenAI)
        create = get_wrapped_call(
            client.chat.completions.create,
            self,
            is_async=True,
            response_type=OpenAICallResponse,
            tool_types=tool_types,
        )
        messages = self._update_messages_if_json(self.messages(), tool_types)
        user_message_param = self._get_possible_user_message(messages)
        start_time = datetime.datetime.now().timestamp() * 1000
        completion = await create(
            messages=messages,
            stream=False,
            **kwargs,
        )
        return OpenAICallResponse(
            response=completion,
            user_message_param=user_message_param,
            tool_types=tool_types,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
            cost=openai_api_calculate_cost(completion.usage, completion.model),
            response_format=self.call_params.response_format,
        )

    @retry
    def stream(
        self, retries: Union[int, Retrying] = 0, **kwargs: Any
    ) -> Generator[OpenAICallResponseChunk, None, None]:
        """Streams the response for a call using this `OpenAICall`.

        Args:
            retries: An integer for the number of times to retry the call or
                a `tenacity.Retrying` instance.
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Yields:
            A `OpenAICallResponseChunk` for each chunk of the response.

        Raises:
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        kwargs, tool_types = self._setup_openai_kwargs(kwargs)
        client = self._setup_openai_client(OpenAI)
        create = get_wrapped_call(
            client.chat.completions.create,
            self,
            response_chunk_type=OpenAICallResponseChunk,
            tool_types=tool_types,
        )
        messages = self._update_messages_if_json(self.messages(), tool_types)
        user_message_param = self._get_possible_user_message(messages)
        if not isinstance(client, AzureOpenAI):
            kwargs["stream_options"] = {"include_usage": True}
        stream = create(
            messages=messages,
            stream=True,
            **kwargs,
        )
        for chunk in stream:
            yield OpenAICallResponseChunk(
                chunk=chunk,
                user_message_param=user_message_param,
                tool_types=tool_types,
                cost=openai_api_calculate_cost(chunk.usage, chunk.model),
                response_format=self.call_params.response_format,
            )

    @retry
    async def stream_async(
        self, retries: Union[int, AsyncRetrying] = 0, **kwargs: Any
    ) -> AsyncGenerator[OpenAICallResponseChunk, None]:
        """Streams the response for an asynchronous call using this `OpenAICall`.

        Args:
            retries: An integer for the number of times to retry the call or
                a `tenacity.AsyncRetrying` instance.
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Yields:
            A `OpenAICallResponseChunk` for each chunk of the response.

        Raises:
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        kwargs, tool_types = self._setup_openai_kwargs(kwargs)
        client = self._setup_openai_client(AsyncOpenAI)
        create = get_wrapped_call(
            client.chat.completions.create,
            self,
            is_async=True,
            response_chunk_type=OpenAICallResponseChunk,
            tool_types=tool_types,
        )
        messages = self._update_messages_if_json(self.messages(), tool_types)
        user_message_param = self._get_possible_user_message(messages)
        if not isinstance(client, AsyncAzureOpenAI):
            kwargs["stream_options"] = {"include_usage": True}
        stream = await create(
            messages=messages,
            stream=True,
            **kwargs,
        )
        async for chunk in stream:
            yield OpenAICallResponseChunk(
                chunk=chunk,
                user_message_param=user_message_param,
                tool_types=tool_types,
                cost=openai_api_calculate_cost(chunk.usage, chunk.model),
                response_format=self.call_params.response_format,
            )

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

    @overload
    def _setup_openai_client(self, client_type: type[OpenAI]) -> OpenAI:
        ...  # pragma: no cover

    @overload
    def _setup_openai_client(self, client_type: type[AsyncOpenAI]) -> AsyncOpenAI:
        ...  # pragma: no cover

    def _setup_openai_client(
        self, client_type: Union[type[OpenAI], type[AsyncOpenAI]]
    ) -> Union[OpenAI, AsyncOpenAI]:
        """Returns the proper OpenAI/AsyncOpenAI client, including wrapping it."""
        using_azure = "inner_azure_client_wrapper" in [
            getattr(wrapper, __name__, None)
            for wrapper in self.configuration.client_wrappers
        ]
        client = client_type(
            api_key=self.api_key if not using_azure else "make-azure-not-fail",
            base_url=self.base_url,
        )
        if client_type == OpenAI:
            client = get_wrapped_client(client, self)
        elif client_type == AsyncOpenAI:
            client = get_wrapped_async_client(client, self)
        return client

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
