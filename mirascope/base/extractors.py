"""A base abstract interface for extracting structured information using LLMs."""
import logging
from abc import ABC, abstractmethod
from enum import Enum
from inspect import getmembers, isclass
from typing import (
    Annotated,
    Any,
    AsyncGenerator,
    Callable,
    ClassVar,
    Generator,
    Generic,
    Literal,
    Optional,
    Type,
    TypeVar,
    Union,
    get_origin,
)

from pydantic import BaseModel, ConfigDict, ValidationError

from ..partial import partial
from .calls import BaseCall
from .prompts import BasePrompt
from .tool_streams import BaseToolStream
from .tools import BaseTool, BaseType
from .types import BaseCallParams

logger = logging.getLogger("mirascope")

BaseModelT = TypeVar("BaseModelT", bound=BaseModel)
BaseCallT = TypeVar("BaseCallT", bound=BaseCall)
BaseToolT = TypeVar("BaseToolT", bound=BaseTool)
BaseToolStreamT = TypeVar("BaseToolStreamT", bound=BaseToolStream)
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


class BaseExtractor(
    BasePrompt, Generic[BaseCallT, BaseToolT, BaseToolStreamT, ExtractedTypeT], ABC
):
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

    # Note: only some model providers support streaming tools, so we only implement
    # streaming for those providers and do not require all extractors to implement
    # the `stream` and `stream_async` methods.
    # @abstractmethod
    # def stream(self, retries: int = 0) -> Generator[ExtractedTypeT, None, None]:
    #     """Streams extracted partial `extraction_schema` instances."""
    #     ...  # pragma: no cover

    # @abstractmethod
    # async def stream_async(
    #     self, retries: int = 0
    # ) -> AsyncGenerator[ExtractedTypeT, None]:
    #     """Asynchronously streams extracted partial `extraction_schema` instances."""
    #     ...  # pragma: no cover

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
            call_type: The type of call to use for extraction. This enables shared code
                across various model providers that have slight variations but the same
                internal interfaces.
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

        temp_call = self._generate_temp_call(call_type)

        response = temp_call(**self.model_dump(exclude={"extract_schema"})).call(
            **kwargs
        )
        try:
            extracted_schema = self._extract_schema(
                response.tool, self.extract_schema, return_tool, response=response
            )
            if extracted_schema is None:
                raise AttributeError("No tool found in the completion.")
            return extracted_schema
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
            call_type: The type of call to use for extraction. This enables shared code
                across various model providers that have slight variations but the same
                internal interfaces.
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

        temp_call = self._generate_temp_call(call_type)

        response = await temp_call(
            **self.model_dump(exclude={"extract_schema"})
        ).call_async(**kwargs)
        try:
            extracted_schema = self._extract_schema(
                response.tool, self.extract_schema, return_tool, response=response
            )
            if extracted_schema is None:
                raise AttributeError("No tool found in the completion.")
            return extracted_schema
        except (AttributeError, ValueError, ValidationError) as e:
            if retries > 0:
                logging.info(f"Retrying due to exception: {e}")
                # TODO: include failure in retry prompt.
                return await self._extract_async(
                    call_type, tool_type, retries - 1, **kwargs
                )
            raise  # re-raise if we have no retries left

    def _stream(
        self,
        call_type: Type[BaseCallT],
        tool_type: Type[BaseToolT],
        tool_stream_type: Type[BaseToolStreamT],
        retries: int,
        **kwargs: Any,
    ) -> Generator[ExtractedTypeT, None, None]:
        """Streams partial `extract_schema` instances from the streamed chunks.

        The `extract_schema` is converted into a partial tool, complete with a
        description of the tool, all of the fields, and their types. This allows us to
        take advantage of tools/function calling functionality to stream information
        extracted from a prompt according to the context provided by the `BaseModel`
        schema.

        Args:
            call_type: The type of call to use for extraction. This enables shared code
                across various model providers that have slight variations but the same
                internal interfaces.
            tool_type: The type of tool to use for extraction. This enables shared code
                across various model providers that have slight variations but the same
                internal interfaces.
            tool_stream_type: The type of tool stream to use for streaming tools. This
                enables shared code across various model providers that have slight
                variations but the same internal interfaces.
            retries: The number of call attempts to make on `ValidationError` before
                giving up and throwing the error to the user.
            **kwargs: Additional keyword arguments.

        Yields:
            An instance of the partial `extract_schema` with it's available fields
            populated.

        Raises:
            AttributeError: if there is no tool in the call creation.
            ValidationError: if the schema cannot be instantiated from the completion.
        """
        kwargs, return_tool = self._setup(tool_type, kwargs)

        temp_call = self._generate_temp_call(call_type)

        stream = temp_call(**self.model_dump(exclude={"extract_schema"})).stream(
            **kwargs
        )
        tool_stream = tool_stream_type.from_stream(stream, allow_partial=True)
        try:
            yielded = False
            for partial_tool in tool_stream:
                extracted_schema = self._extract_schema(
                    partial_tool, self.extract_schema, return_tool, response=None
                )
                if extracted_schema is None:
                    break
                yielded = True
                yield extracted_schema

            if not yielded:
                raise AttributeError("No tool found in the completion.")
        except (AttributeError, ValueError, ValidationError) as e:
            if retries > 0:
                logging.info(f"Retrying due to exception: {e}")
                # TODO: include failure in retry prompt.
                yield from self._stream(
                    call_type, tool_type, tool_stream_type, retries - 1, **kwargs
                )
            raise  # re-raise if we have no retries left

    async def _stream_async(
        self,
        call_type: Type[BaseCallT],
        tool_type: Type[BaseToolT],
        tool_stream_type: Type[BaseToolStreamT],
        retries: int,
        **kwargs: Any,
    ) -> AsyncGenerator[ExtractedTypeT, None]:
        """Asynchronously streams partial `extract_schema`s from streamed chunks.

        The `extract_schema` is converted into a partial tool, complete with a
        description of the tool, all of the fields, and their types. This allows us to
        take advantage of tools/function calling functionality to stream information
        extracted from a prompt according to the context provided by the `BaseModel`
        schema.

        Args:
            call_type: The type of call to use for extraction. This enables shared code
                across various model providers that have slight variations but the same
                internal interfaces.
            tool_type: The type of tool to use for extraction. This enables shared code
                across various model providers that have slight variations but the same
                internal interfaces.
            tool_stream_type: The type of tool stream to use for streaming tools. This
                enables shared code across various model providers that have slight
                variations but the same internal interfaces.
            retries: The number of call attempts to make on `ValidationError` before
                giving up and throwing the error to the user.
            **kwargs: Additional keyword arguments.

        Yields:
            An instance of the partial `extract_schema` with it's available fields
            populated.

        Raises:
            AttributeError: if there is no tool in the call creation.
            ValidationError: if the schema cannot be instantiated from the completion.
        """
        kwargs, return_tool = self._setup(tool_type, kwargs)

        temp_call = self._generate_temp_call(call_type)

        stream = temp_call(**self.model_dump(exclude={"extract_schema"})).stream_async(
            **kwargs
        )
        tool_stream = tool_stream_type.from_async_stream(stream, allow_partial=True)
        try:
            yielded = False
            async for partial_tool in tool_stream:
                extracted_schema = self._extract_schema(
                    partial_tool, self.extract_schema, return_tool, response=None
                )
                if extracted_schema is None:
                    break
                yielded = True
                yield extracted_schema

            if not yielded:
                raise AttributeError("No tool found in the completion.")
        except (AttributeError, ValueError, ValidationError) as e:
            if retries > 0:
                logging.info(f"Retrying due to exception: {e}")
                # TODO: include failure in retry prompt.
                async for partial_tool in self._stream_async(
                    call_type, tool_type, tool_stream_type, retries - 1, **kwargs
                ):
                    yield partial_tool
            raise  # re-raise if we have no retries left

    def _generate_temp_call(self, call_type: Type[BaseCallT]) -> Type[BaseCallT]:
        """Returns a `TempCall` generated using the extractors definition."""

        class TempCall(call_type):  # type: ignore
            prompt_template = self.prompt_template

            base_url = self.base_url
            api_key = self.api_key
            call_params = self.call_params

            model_config = ConfigDict(extra="allow")

        properties = getmembers(self)
        for name, value in properties:
            if not hasattr(TempCall, name):
                setattr(TempCall, name, value)

        return TempCall

    def _extract_schema(
        self,
        tool: Optional[BaseToolT],
        schema: ExtractedType,
        return_tool: bool,
        response: Optional[Any],
    ) -> Optional[ExtractedTypeT]:
        """Returns the extracted schema extracted depending on it's extraction type.

        Due to mypy issues with all these generics, we have to type ignore a bunch
        of stuff so it doesn't complain, but each conditional properly checks types
        before doing anything specific to that type (it's just that mypy is annoying).
        """
        if tool is None:
            return None
        if return_tool:
            return tool  # type: ignore
        if _is_base_type(schema):
            return tool.value  # type: ignore
        if response:
            model = schema(**tool.model_dump())  # type: ignore
            model._response = response
        else:
            schema = partial(schema)  # type: ignore
            model = schema(**tool.model_dump())
            model._tool_call = tool.tool_call  # type: ignore
        return model

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
