"""A module for calling Google's Gemini Chat API."""
import datetime
import logging
from typing import (
    Any,
    AsyncGenerator,
    ClassVar,
    Generator,
    Union,
)

from google.generativeai import GenerativeModel  # type: ignore
from google.generativeai.types import ContentsType  # type: ignore
from tenacity import AsyncRetrying, Retrying

from ..base import BaseCall, retry
from ..enums import MessageRole
from .tools import GeminiTool
from .types import (
    GeminiCallParams,
    GeminiCallResponse,
    GeminiCallResponseChunk,
)

logger = logging.getLogger("mirascope")


class GeminiCall(BaseCall[GeminiCallResponse, GeminiCallResponseChunk, GeminiTool]):
    '''A class for prompting Google's Gemini Chat API.

    This prompt supports the message types: USER, MODEL, TOOL

    Example:

    ```python
    from google.generativeai import configure  # type: ignore
    from mirascope.gemini import GeminiCall

    configure(api_key="YOUR_API_KEY")


    class BookRecommender(GeminiCall):
        prompt_template = """
        USER: You're the world's greatest librarian.
        MODEL: Ok, I understand I'm the world's greatest librarian. How can I help?
        USER: Please recommend some {genre} books.

        genre: str


    response = BookRecommender(genre="fantasy").call()
    print(response.content)
    #> As the world's greatest librarian, I am delighted to recommend...
    ```
    '''

    call_params: ClassVar[GeminiCallParams] = GeminiCallParams()

    def messages(self) -> ContentsType:
        """Returns the `ContentsType` messages for Gemini `generate_content`.

        Raises:
            ValueError: if the docstring contains an unknown role.
        """
        return [
            {"role": message["role"], "parts": [message["content"]]}
            for message in self._parse_messages(
                [MessageRole.MODEL, MessageRole.USER, MessageRole.TOOL]
            )
        ]

    @retry
    def call(
        self, retries: Union[int, Retrying] = 0, **kwargs: Any
    ) -> GeminiCallResponse:
        """Makes an call to the model using this `GeminiCall` instance.

        Args:
            **kwargs: Additional keyword arguments that will be used for generating the
                response. These will override any existing argument settings in call
                params.

        Returns:
            A `GeminiCallResponse` instance.
        """
        kwargs, tool_types = self._setup(kwargs, GeminiTool)
        model_name = kwargs.pop("model")
        gemini_pro_model = GenerativeModel(model_name=model_name)
        generate_content = gemini_pro_model.generate_content
        if self.call_params.weave is not None:
            generate_content = self.call_params.weave(
                generate_content
            )  # pragma: no cover
        if self.call_params.logfire:  # pragma: no cover
            generate_content = self.call_params.logfire(
                generate_content,
                "gemini",
                response_type=GeminiCallResponse,
                tool_types=tool_types,
            )
            kwargs["model"] = model_name
        if self.call_params.langfuse:  # pragma: no cover
            generate_content = self.call_params.langfuse(
                generate_content,
                "gemini",
                response_type=GeminiCallResponse,
            )  # pragma: no cover
            kwargs["model"] = model_name
        start_time = datetime.datetime.now().timestamp() * 1000
        response = generate_content(
            self.messages(),
            stream=False,
            tools=kwargs.pop("tools") if "tools" in kwargs else None,
            **kwargs,
        )
        return GeminiCallResponse(
            response=response,
            tool_types=tool_types,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
            cost=None,
        )

    @retry
    async def call_async(
        self, retries: Union[int, AsyncRetrying] = 0, **kwargs: Any
    ) -> GeminiCallResponse:
        """Makes an asynchronous call to the model using this `GeminiCall` instance.

        Args:
            **kwargs: Additional keyword arguments that will be used for generating the
                response. These will override any existing argument settings in call
                params.

        Returns:
            A `GeminiCallResponse` instance.
        """
        kwargs, tool_types = self._setup(kwargs, GeminiTool)
        model_name = kwargs.pop("model")
        gemini_pro_model = GenerativeModel(model_name=model_name)
        generate_content_async = gemini_pro_model.generate_content_async
        if self.call_params.weave is not None:
            generate_content_async = self.call_params.weave(
                generate_content_async
            )  # pragma: no cover
        if self.call_params.logfire:
            generate_content_async = self.call_params.logfire(
                generate_content_async,
                "gemini",
                response_type=GeminiCallResponse,
                tool_types=tool_types,
            )  # pragma: no cover
            kwargs["model"] = model_name  # pragma: no cover
        start_time = datetime.datetime.now().timestamp() * 1000
        response = await generate_content_async(
            self.messages(),
            stream=False,
            tools=kwargs.pop("tools") if "tools" in kwargs else None,
            **kwargs,
        )
        return GeminiCallResponse(
            response=response,
            tool_types=tool_types,
            start_time=start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
            cost=None,
        )

    @retry
    def stream(
        self, retries: Union[int, Retrying] = 0, **kwargs: Any
    ) -> Generator[GeminiCallResponseChunk, None, None]:
        """Streams the response for a call using this `GeminiCall`.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Yields:
            A `GeminiCallResponseChunk` for each chunk of the response.
        """
        kwargs, tool_types = self._setup(kwargs, GeminiTool)
        model_name = kwargs.pop("model")
        gemini_pro_model = GenerativeModel(model_name=model_name)
        generate_content = gemini_pro_model.generate_content
        if self.call_params.logfire:
            generate_content = self.call_params.logfire(
                generate_content, "gemini", response_chunk_type=GeminiCallResponseChunk
            )  # pragma: no cover
            kwargs["model"] = model_name  # pragma: no cover
        stream = generate_content(
            self.messages(),
            stream=True,
            tools=kwargs.pop("tools") if "tools" in kwargs else None,
            **kwargs,
        )
        for chunk in stream:
            yield GeminiCallResponseChunk(chunk=chunk, tool_types=tool_types)

    @retry
    async def stream_async(
        self, retries: Union[int, AsyncRetrying] = 0, **kwargs: Any
    ) -> AsyncGenerator[GeminiCallResponseChunk, None]:
        """Streams the response asynchronously for a call using this `GeminiCall`.

        Args:
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Yields:
            A `GeminiCallResponseChunk` for each chunk of the response.
        """
        kwargs, tool_types = self._setup(kwargs, GeminiTool)
        model_name = kwargs.pop("model")
        gemini_pro_model = GenerativeModel(model_name=model_name)
        generate_content_async = gemini_pro_model.generate_content_async
        if self.call_params.logfire:
            generate_content_async = self.call_params.logfire(
                generate_content_async,
                "gemini",
                response_chunk_type=GeminiCallResponseChunk,
            )  # pragma: no cover
            kwargs["model"] = model_name  # pragma: no cover
        stream = await generate_content_async(
            self.messages(),
            stream=True,
            tools=kwargs.pop("tools") if "tools" in kwargs else None,
            **kwargs,
        )
        async for chunk in stream:
            yield GeminiCallResponseChunk(chunk=chunk, tool_types=tool_types)
