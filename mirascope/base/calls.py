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
    Union,
    cast,
)

from pydantic import create_model
from tenacity import AsyncRetrying, Retrying

from .prompts import BasePrompt, BasePromptT
from .tools import BaseTool
from .types import (
    BaseCallParams,
    BaseCallResponse,
    BaseCallResponseChunk,
    BaseConfig,
)

BaseCallResponseT = TypeVar("BaseCallResponseT", bound=BaseCallResponse)
BaseCallResponseChunkT = TypeVar("BaseCallResponseChunkT", bound=BaseCallResponseChunk)
BaseToolT = TypeVar("BaseToolT", bound=BaseTool)
MessageParamT = TypeVar("MessageParamT", bound=Any)


class BaseCall(
    BasePrompt,
    Generic[BaseCallResponseT, BaseCallResponseChunkT, BaseToolT, MessageParamT],
    ABC,
):
    """The base class abstract interface for calling LLMs."""

    api_key: ClassVar[Optional[str]] = None
    base_url: ClassVar[Optional[str]] = None
    call_params: ClassVar[BaseCallParams] = BaseCallParams[BaseToolT](
        model="gpt-3.5-turbo-0125"
    )
    configuration: ClassVar[BaseConfig] = BaseConfig(llm_ops=[], client_wrappers=[])
    _provider: ClassVar[str] = "base"

    @abstractmethod
    def call(
        self, retries: Union[int, Retrying] = 0, **kwargs: Any
    ) -> BaseCallResponseT:
        """A call to an LLM.

        An implementation of this function must return a response that extends
        `BaseCallResponse`. This ensures a consistent API and convenience across e.g.
        different model providers.
        """
        ...  # pragma: no cover

    @abstractmethod
    async def call_async(
        self, retries: Union[int, AsyncRetrying] = 0, **kwargs: Any
    ) -> BaseCallResponseT:
        """An asynchronous call to an LLM.

        An implementation of this function must return a response that extends
        `BaseCallResponse`. This ensures a consistent API and convenience across e.g.
        different model providers.
        """
        ...  # pragma: no cover

    @abstractmethod
    def stream(
        self, retries: Union[int, Retrying] = 0, **kwargs: Any
    ) -> Generator[BaseCallResponseChunkT, None, None]:
        """A call to an LLM that streams the response in chunks.

        An implementation of this function must yield response chunks that extend
        `BaseCallResponseChunk`. This ensures a consistent API and convenience across
        e.g. different model providers.
        """
        ...  # pragma: no cover

    @abstractmethod
    async def stream_async(
        self, retries: Union[int, AsyncRetrying] = 0, **kwargs: Any
    ) -> AsyncGenerator[BaseCallResponseChunkT, None]:
        """A asynchronous call to an LLM that streams the response in chunks.

        An implementation of this function must yield response chunks that extend
        `BaseCallResponseChunk`. This ensures a consistent API and convenience across
        e.g. different model providers."""
        yield ...  # type: ignore # pragma: no cover

    @classmethod
    def from_prompt(
        cls, prompt_type: type[BasePromptT], call_params: BaseCallParams
    ) -> type[BasePromptT]:
        """Returns a call_type generated dynamically from this base call.

        Args:
            prompt_type: The prompt class to use for the call. Properties and class
                variables of this class will be used to create the new call class. Must
                be a class that can be instantiated.
            call_params: The call params to use for the call.

        Returns:
            A new call class with new call_type.
        """

        fields: dict[str, Any] = {
            name: (field.annotation, field.default)
            for name, field in prompt_type.model_fields.items()
        }

        class_vars = {
            name: value
            for name, value in prompt_type.__dict__.items()
            if name not in prompt_type.model_fields
        }
        new_call = create_model(prompt_type.__name__, __base__=cls, **fields)

        for var_name, var_value in class_vars.items():
            setattr(new_call, var_name, var_value)
        setattr(new_call, "call_params", call_params)

        return cast(type[BasePromptT], new_call)

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

    def _get_possible_user_message(
        self, messages: list[Any]
    ) -> Optional[MessageParamT]:
        """Returns the most recent message if it's a user message, otherwise `None`."""
        return messages[-1] if messages[-1]["role"] == "user" else None


BaseCallT = TypeVar("BaseCallT", bound=BaseCall)
