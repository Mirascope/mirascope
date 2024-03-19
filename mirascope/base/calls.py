"""A base abstract interface for calling LLMs."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    Any,
    AsyncGenerator,
    ClassVar,
    Generator,
    Generic,
    Optional,
    Type,
    TypeVar,
)

from .prompts import BasePrompt
from .tools import BaseTool
from .types import BaseCallParams, BaseCallResponse, BaseCallResponseChunk

BaseCallResponseT = TypeVar("BaseCallResponseT", bound=BaseCallResponse)
BaseCallResponseChunkT = TypeVar("BaseCallResponseChunkT", bound=BaseCallResponseChunk)
BaseToolT = TypeVar("BaseToolT", bound=BaseTool)


class BaseCall(
    BasePrompt, Generic[BaseCallResponseT, BaseCallResponseChunkT, BaseToolT], ABC
):
    """The base class abstract interface for calling LLMs."""

    api_key: ClassVar[Optional[str]] = None
    base_url: ClassVar[Optional[str]] = None
    call_params: ClassVar[BaseCallParams] = BaseCallParams[BaseToolT](
        model="gpt-3.5-turbo-0125"
    )

    @abstractmethod
    def call(self, **kwargs: Any) -> BaseCallResponseT:
        """A call to an LLM.

        An implementation of this function must return a response that extends
        `BaseCallResponse`. This ensures a consistent API and convenience across e.g.
        different model providers.
        """
        ...  # pragma: no cover

    @abstractmethod
    async def call_async(self, **kwargs: Any) -> BaseCallResponseT:
        """An asynchronous call to an LLM.

        An implementation of this function must return a response that extends
        `BaseCallResponse`. This ensures a consistent API and convenience across e.g.
        different model providers.
        """
        ...  # pragma: no cover

    @abstractmethod
    def stream(self, **kwargs: Any) -> Generator[BaseCallResponseChunkT, None, None]:
        """A call to an LLM that streams the response in chunks.

        An implementation of this function must yield response chunks that extend
        `BaseCallResponseChunk`. This ensures a consistent API and convenience across
        e.g. different model providers.
        """
        ...  # pragma: no cover

    @abstractmethod
    async def stream_async(
        self, **kwargs: Any
    ) -> AsyncGenerator[BaseCallResponseChunkT, None]:
        """A asynchronous call to an LLM that streams the response in chunks.

        An implementation of this function must yield response chunks that extend
        `BaseCallResponseChunk`. This ensures a consistent API and convenience across
        e.g. different model providers."""
        yield ...  # type: ignore # pragma: no cover

    ############################## PRIVATE METHODS ###################################

    def _setup(
        self,
        kwargs: dict[str, Any],
        base_tool_type: Optional[Type[BaseToolT]] = None,
    ) -> tuple[dict[str, Any], Optional[list[Type[BaseToolT]]]]:
        """Returns the call params kwargs and tool types.

        The tools in the call params first get converted into BaseToolT types. We then
        need both the converted tools for the response (so it can construct actual tool
        instances if present in the response) as well as the actual schemas injected
        through kwargs. This function handles that setup.
        """
        call_params = self.call_params.model_copy(update=kwargs)
        kwargs = call_params.kwargs(tool_type=base_tool_type)
        tool_types = None
        if "tools" in kwargs and base_tool_type is not None:
            tool_types = kwargs.pop("tools")
            kwargs["tools"] = [tool_type.tool_schema() for tool_type in tool_types]
        return kwargs, tool_types
