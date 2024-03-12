"""A module for calling OpenAI's Chat Completion models."""
import datetime
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

from openai import AsyncOpenAI, OpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionUserMessageParam,
)

from ..base import BaseCall, BasePrompt
from .tools import OpenAITool
from .types import OpenAICallParams, OpenAICallResponse, OpenAICallResponseChunk


class OpenAICall(BaseCall[OpenAICallResponse, OpenAICallResponseChunk], BasePrompt):
    """A base class for calling OpenAI's Chat Completion models.

    Example:

    ```python
    from mirascope.openai import OpenAICall


    class BookRecommender(OpenAICall):
        template = "Please recommend a {genre} book"

        genre: str

    book = BookRecommender(genre="fantasy").call()
    print(book)
    #> There are many great books to read, it ultimately depends...
    ```
    """

    call_params: ClassVar[OpenAICallParams] = OpenAICallParams(
        model="gpt-3.5-turbo-0125"
    )

    def messages(self) -> list[ChatCompletionMessageParam]:
        """Returns the template as a formatted list of messages."""
        message_type_by_role = {
            "system": ChatCompletionSystemMessageParam,
            "user": ChatCompletionUserMessageParam,
            "assistant": ChatCompletionAssistantMessageParam,
            "tool": ChatCompletionToolMessageParam,
        }
        return [
            message_type_by_role[role](role=role, content=content)
            for role, content in self._parse_messages(list(message_type_by_role.keys()))
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
        client, kwargs, tool_types = self._setup(OpenAI(base_url=self.base_url), kwargs)
        start_time = datetime.datetime.now().timestamp() * 1000
        completion = client.chat.completions.create(
            messages=self.messages(),
            stream=False,
            **kwargs,
        )
        return OpenAICallResponse(
            response=completion,
            tool_types=tool_types,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
        )

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
        client, kwargs, tool_types = self._setup(
            AsyncOpenAI(base_url=self.base_url), kwargs
        )
        start_time = datetime.datetime.now().timestamp() * 1000
        completion = await client.chat.completions.create(
            messages=self.messages(),
            stream=False,
            **kwargs,
        )
        return OpenAICallResponse(
            response=completion,
            tool_types=tool_types,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
        )

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
        client, kwargs, tool_types = self._setup(OpenAI(base_url=self.base_url), kwargs)
        stream = client.chat.completions.create(
            messages=self.messages(),
            stream=True,
            **kwargs,
        )
        for chunk in stream:
            yield OpenAICallResponseChunk(chunk=chunk, tool_types=tool_types)

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
        client, kwargs, tool_types = self._setup(
            AsyncOpenAI(base_url=self.base_url), kwargs
        )
        stream = await client.chat.completions.create(
            messages=self.messages(),
            stream=True,
            **kwargs,
        )
        async for chunk in stream:
            yield OpenAICallResponseChunk(chunk=chunk, tool_types=tool_types)

    ############################## PRIVATE METHODS ###################################

    @overload
    def _setup(
        self, client: OpenAI, kwargs: dict[str, Any]
    ) -> tuple[OpenAI, dict[str, Any], Optional[list[Type[OpenAITool]]]]:
        ...  # pragma: no cover

    @overload
    def _setup(
        self, client: AsyncOpenAI, kwargs: dict[str, Any]
    ) -> tuple[AsyncOpenAI, dict[str, Any], Optional[list[Type[OpenAITool]]]]:
        ...  # pragma: no cover

    def _setup(
        self,
        client: Union[AsyncOpenAI, OpenAI],
        kwargs: dict[str, Any],
    ) -> tuple[
        Union[AsyncOpenAI, OpenAI], dict[str, Any], Optional[list[Type[OpenAITool]]]
    ]:
        """Returns the call params kwargs and tool types.

        The tools in the call params first get converted into OpenAI tools. We then need
        both the converted tools for the response (so it can construct tools if present
        in the response) as well as the actual schemas injected through kwargs. This
        function handles that setup.
        """
        call_params = self.call_params.model_copy(update=kwargs)
        if call_params.wrapper is not None:
            client = call_params.wrapper(client)  # type: ignore
        kwargs = call_params.kwargs()
        tool_types = None
        if "tools" in kwargs:
            tool_types = kwargs.pop("tools")
            kwargs["tools"] = [tool.tool_schema() for tool in tool_types]
        return client, kwargs, tool_types
