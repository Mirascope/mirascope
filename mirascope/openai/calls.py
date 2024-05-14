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
)

from openai import AsyncOpenAI, OpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.completion_create_params import ResponseFormat
from tenacity import AsyncRetrying, Retrying

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
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        if self.call_params.langfuse:  # pragma: no cover
            from langfuse.openai import OpenAI as LangfuseOpenAI

            client = LangfuseOpenAI(api_key=self.api_key, base_url=self.base_url)
        if self.call_params.wrapper is not None:
            client = self.call_params.wrapper(client)
        if self.call_params.logfire:
            self.call_params.logfire(client)  # pragma: no cover
        create = client.chat.completions.create
        messages = self._update_messages_if_json(self.messages(), tool_types)
        start_time = datetime.datetime.now().timestamp() * 1000
        completion = create(
            messages=messages,
            stream=False,
            **kwargs,
        )
        return OpenAICallResponse(
            response=completion,
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
        client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        if self.call_params.langfuse:  # pragma: no cover
            from langfuse.openai import AsyncOpenAI as LangfuseAsyncOpenAI

            client = LangfuseAsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        if self.call_params.wrapper_async is not None:
            client = self.call_params.wrapper_async(client)
        if self.call_params.logfire:
            self.call_params.logfire(client)  # pragma: no cover
        messages = self._update_messages_if_json(self.messages(), tool_types)
        start_time = datetime.datetime.now().timestamp() * 1000
        completion = await client.chat.completions.create(
            messages=messages,
            stream=False,
            **kwargs,
        )
        return OpenAICallResponse(
            response=completion,
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
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        if self.call_params.langfuse:  # pragma: no cover
            from langfuse.openai import OpenAI as LangfuseOpenAI

            client = LangfuseOpenAI(api_key=self.api_key, base_url=self.base_url)
        if self.call_params.wrapper is not None:
            client = self.call_params.wrapper(client)
        if self.call_params.logfire:
            self.call_params.logfire(client)  # pragma: no cover
        messages = self._update_messages_if_json(self.messages(), tool_types)
        stream = client.chat.completions.create(
            messages=messages,
            stream=True,
            stream_options={"include_usage": True},
            **kwargs,
        )
        for chunk in stream:
            yield OpenAICallResponseChunk(
                chunk=chunk,
                tool_types=tool_types,
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
        client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        if self.call_params.langfuse:  # pragma: no cover
            from langfuse.openai import AsyncOpenAI as LangfuseAsyncOpenAI

            client = LangfuseAsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        if self.call_params.wrapper_async is not None:
            client = self.call_params.wrapper_async(client)
        if self.call_params.logfire:
            self.call_params.logfire(client)  # pragma: no cover
        messages = self._update_messages_if_json(self.messages(), tool_types)
        stream = await client.chat.completions.create(
            messages=messages,
            stream=True,
            stream_options={"include_usage": True},
            **kwargs,
        )
        async for chunk in stream:
            yield OpenAICallResponseChunk(
                chunk=chunk,
                tool_types=tool_types,
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
