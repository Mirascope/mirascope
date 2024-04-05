"""A module for calling Groq's Cloud API."""
import datetime
import json
from typing import Any, AsyncGenerator, ClassVar, Generator, Optional, Type

from groq import AsyncGroq, Groq
from groq.types.chat.completion_create_params import Message, ResponseFormat

from ..base import BaseCall
from ..enums import MessageRole
from .tools import GroqTool
from .types import GroqCallParams, GroqCallResponse, GroqCallResponseChunk

JSON_MODE_CONTENT = """
Extract a valid JSON object instance from to content using the following schema:

{schema}
""".strip()


def _json_mode_content(tool_type: Type[GroqTool]) -> str:
    """Returns the formatted `JSON_MODE_CONTENT` with the given tool type."""
    return JSON_MODE_CONTENT.format(
        schema=json.dumps(tool_type.model_json_schema(), indent=2)
    )


class GroqCall(BaseCall[GroqCallResponse, GroqCallResponseChunk, GroqTool]):
    """A base class for calling Groq's Cloud API.

    Example:

    ```python
    from mirascope.groq import GroqCall


    class BookRecommender(GroqCall):
        prompt_template = "Please recommend a {genre} book"

        genre: str

    response = BookRecommender(genre="fantasy").call()
    print(response.content)
    #> There are many great books to read, it ultimately depends...
    ```
    """

    call_params: ClassVar[GroqCallParams] = GroqCallParams()

    def messages(self) -> list[Message]:
        """Returns the template as a formatted list of messages."""
        return [
            Message(role=message["role"], content=message["content"])
            for message in self._parse_messages(
                [MessageRole.SYSTEM, MessageRole.USER, MessageRole.ASSISTANT]
            )
        ]

    def call(self, **kwargs: Any) -> GroqCallResponse:
        """Makes a call to the model using this `GroqCall` instance.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Returns:
            A `GroqCallResponse` instance.
        """
        kwargs, tool_types = self._setup_groq_kwargs(kwargs)
        client = Groq(api_key=self.api_key, base_url=self.base_url)
        create = client.chat.completions.create
        if self.call_params.weave is not None:
            create = self.call_params.weave(
                client.chat.completions.create
            )  # pragma: no cover
        messages = self._update_messages_if_json(self.messages(), tool_types)
        start_time = datetime.datetime.now().timestamp() * 1000
        completion = create(messages=messages, stream=False, **kwargs)
        return GroqCallResponse(
            response=completion,
            tool_types=tool_types,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
            response_format=self.call_params.response_format,
        )

    async def call_async(self, **kwargs: Any) -> GroqCallResponse:
        """Makes an asynchronous call to the model using this `GroqCall`.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Returns:
            An `GroqCallResponse` instance.
        """
        kwargs, tool_types = self._setup_groq_kwargs(kwargs)
        client = AsyncGroq(api_key=self.api_key, base_url=self.base_url)
        create = client.chat.completions.create
        if self.call_params.weave is not None:
            create = self.call_params.weave(
                client.chat.completions.create
            )  # pragma: no cover
        messages = self._update_messages_if_json(self.messages(), tool_types)
        start_time = datetime.datetime.now().timestamp() * 1000
        completion = await create(messages=messages, stream=False, **kwargs)
        return GroqCallResponse(
            response=completion,
            tool_types=tool_types,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
            response_format=self.call_params.response_format,
        )

    def stream(self, **kwargs: Any) -> Generator[GroqCallResponseChunk, None, None]:
        """Streams the response for a call using this `GroqCall`.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Yields:
            A `GroqCallResponseChunk` for each chunk of the response.
        """
        kwargs, tool_types = self._setup_groq_kwargs(kwargs)
        client = Groq(api_key=self.api_key, base_url=self.base_url)
        messages = self._update_messages_if_json(self.messages(), tool_types)
        stream = client.chat.completions.create(
            messages=messages, stream=True, **kwargs
        )
        for completion in stream:
            yield GroqCallResponseChunk(
                chunk=completion,
                tool_types=tool_types,
                response_format=self.call_params.response_format,
            )

    async def stream_async(
        self, **kwargs: Any
    ) -> AsyncGenerator[GroqCallResponseChunk, None]:
        """Streams the response for an asynchronous call using this `GroqCall`.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Yields:
            A `GroqCallResponseChunk` for each chunk of the response.
        """
        kwargs, tool_types = self._setup_groq_kwargs(kwargs)
        client = AsyncGroq(api_key=self.api_key, base_url=self.base_url)
        messages = self._update_messages_if_json(self.messages(), tool_types)
        stream = await client.chat.completions.create(
            messages=messages, stream=True, **kwargs
        )
        async for completion in stream:
            yield GroqCallResponseChunk(
                chunk=completion,
                tool_types=tool_types,
                response_format=self.call_params.response_format,
            )

    ############################## PRIVATE METHODS ###################################

    def _setup_groq_kwargs(
        self,
        kwargs: dict[str, Any],
    ) -> tuple[
        dict[str, Any],
        Optional[list[Type[GroqTool]]],
    ]:
        """Overrides the `BaseCall._setup` for Groq specific setup."""
        kwargs, tool_types = self._setup(kwargs, GroqTool)
        if (
            self.call_params.response_format == ResponseFormat(type="json_object")
            and tool_types
        ):
            kwargs.pop("tools")
        return kwargs, tool_types

    def _update_messages_if_json(
        self,
        messages: list[Message],
        tool_types: Optional[list[type[GroqTool]]],
    ) -> list[Message]:
        if (
            self.call_params.response_format == ResponseFormat(type="json_object")
            and tool_types
        ):
            messages.append(
                Message(
                    role="user", content=_json_mode_content(tool_type=tool_types[0])
                )
            )
        return messages
