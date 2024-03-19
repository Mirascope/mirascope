"""A base abstract interface for extracting structured information using LLMs."""
import logging
from abc import ABC, abstractmethod
from enum import Enum
from inspect import isclass
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Generic,
    Literal,
    Optional,
    Type,
    TypeVar,
    Union,
    get_origin,
)

from pydantic import BaseModel, ConfigDict, ValidationError

from .calls import BaseCall
from .prompts import BasePrompt
from .tools import BaseTool, BaseType
from .types import BaseCallParams

logger = logging.getLogger("mirascope")

BaseModelT = TypeVar("BaseModelT", bound=BaseModel)
BaseCallT = TypeVar("BaseCallT", bound=BaseCall)
BaseToolT = TypeVar("BaseToolT", bound=BaseTool)
ExtractionType = Union[Type[BaseType], Type[BaseModel], Callable]
ExtractedType = Union[BaseType, BaseModelT, BaseToolT]
ExtractedTypeT = TypeVar("ExtractedTypeT", bound=ExtractedType)


def _is_base_type(type_: Any) -> bool:
    """Check if a type is a base type."""
    base_types = {str, int, float, bool, list, set, tuple}
    return (
        (isclass(type_) and issubclass(type_, Enum))
        or type_ in base_types
        or get_origin(type_) in base_types.union({Literal, Union, Annotated})
    )


class BaseExtractor(BasePrompt, Generic[BaseCallT, BaseToolT, ExtractedTypeT], ABC):
    """The base abstract interface for extracting structured information using LLMs."""

    extract_schema: ExtractionType

    api_key: ClassVar[Optional[str]] = None
    base_url: ClassVar[Optional[str]] = None
    call_params: ClassVar[BaseCallParams] = BaseCallParams[BaseToolT](
        model="gpt-3.5-turbo-0125"
    )

    @abstractmethod
    def extract(self, retries: int = 0) -> ExtractedTypeT:
        """Extracts the `extraction_schema` from an LLM call."""
        ...  # pragma: no cover

    @abstractmethod
    async def extract_async(self, retries: int = 0) -> ExtractedTypeT:
        """Asynchronously extracts the `extraction_schema` from an LLM call."""
        ...  # pragma: no cover

    ############################## PRIVATE METHODS ###################################

    def _extract(
        self,
        call_type: Type[BaseCallT],
        tool_type: Type[BaseToolT],
        retries: int,
        **kwargs: Any,
    ) -> ExtractedTypeT:
        """Extracts `extract_schema` from the call response.

        The `extract_schema` is converted into a tool, complete with a description of
        the tool, all of the fields, and their types. This allows us to take advantage
        of tools/function calling functionality to extract information from a prompt
        according to the context provided by the `BaseModel` schema.

        Args:
            tool_type: The type of tool to use for extraction. This enables shared code
                across various model providers that have slight variations but the same
                internal interfaces.
            retries: The number of call attempts to make on `ValidationError` before
                giving up and throwing the error to the user.
            **kwargs: Additional keyword arguments.

        Returns:
            An instance of the `extract_schema` with it's fields populated.

        Raises:
            AttributeError: if there is no tool in the call creation.
            ValidationError: if the schema cannot be instantiated from the completion.
        """
        kwargs, return_tool = self._setup(tool_type, kwargs)

        class TempCall(call_type):  # type: ignore
            prompt_template = self.prompt_template

            call_params = call_type.call_params

            model_config = ConfigDict(extra="allow")

        response = TempCall(**self.model_dump(exclude={"extract_schema"})).call(
            **kwargs
        )
        try:
            tool = response.tool
            if tool is None:
                raise AttributeError("No tool found in the completion.")
            if return_tool:
                return tool
            if _is_base_type(self.extract_schema):
                return tool.value
            model = self.extract_schema(**response.tool.model_dump())
            model._response = response  # type: ignore
            return model  # type: ignore
        except (AttributeError, ValueError, ValidationError) as e:
            if retries > 0:
                logging.info(f"Retrying due to exception: {e}")
                # TODO: include failure in retry prompt.
                return self._extract(call_type, tool_type, retries - 1, **kwargs)
            raise  # re-raise if we have no retries left

    async def _extract_async(
        self,
        call_type: Type[BaseCallT],
        tool_type: Type[BaseToolT],
        retries: int,
        **kwargs: Any,
    ) -> ExtractedTypeT:
        """Extracts `extract_schema` from the asynchronous call response.

        The `extract_schema` is converted into a tool, complete with a description of
        the tool, all of the fields, and their types. This allows us to take advantage
        of tools/function calling functionality to extract information from a prompt
        according to the context provided by the `BaseModel` schema.

        Args:
            tool_type: The type of tool to use for extraction. This enables shared code
                across various model providers that have slight variations but the same
                internal interfaces.
            retries: The number of call attempts to make on `ValidationError` before
                giving up and throwing the error to the user.
            **kwargs: Additional keyword arguments.

        Returns:
            An instance of the `extract_schema` with it's fields populated.

        Raises:
            AttributeError: if there is no tool in the call creation.
            ValidationError: if the schema cannot be instantiated from the completion.
        """
        kwargs, return_tool = self._setup(tool_type, kwargs)

        class TempCall(call_type):  # type: ignore
            prompt_template = self.prompt_template

            call_params = call_type.call_params

            model_config = ConfigDict(extra="allow")

        response = await TempCall(
            **self.model_dump(exclude={"extract_schema"})
        ).call_async(**kwargs)
        try:
            tool = response.tool
            if tool is None:
                raise AttributeError("No tool found in the completion.")
            if return_tool:
                return tool
            if _is_base_type(self.extract_schema):
                return tool.value
            model = self.extract_schema(**response.tool.model_dump())
            model._response = response  # type: ignore
            return model  # type: ignore
        except (AttributeError, ValueError, ValidationError) as e:
            if retries > 0:
                logging.info(f"Retrying due to exception: {e}")
                # TODO: include failure in retry prompt.
                return await self._extract_async(
                    call_type, tool_type, retries - 1, **kwargs
                )
            raise  # re-raise if we have no retries left

    def _setup(
        self, tool_type: Type[BaseToolT], kwargs: dict[str, Any]
    ) -> tuple[dict[str, Any], bool]:
        """Returns the call params kwargs and whether to return the tool directly."""
        call_params = self.call_params.model_copy(update=kwargs)
        kwargs = call_params.kwargs(tool_type=tool_type)
        if _is_base_type(self.extract_schema):
            tool = tool_type.from_base_type(self.extract_schema)  # type: ignore
            return_tool = False
        elif not isclass(self.extract_schema):
            tool = tool_type.from_fn(self.extract_schema)
            return_tool = True
        elif not issubclass(self.extract_schema, tool_type):
            tool = tool_type.from_model(self.extract_schema)
            return_tool = False
        else:
            tool = self.extract_schema
            return_tool = True
        kwargs["tools"] = [tool]
        return kwargs, return_tool
