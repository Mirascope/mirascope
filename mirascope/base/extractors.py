"""A base abstract interface for extracting structured information using LLMs."""
from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import suppress
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
    cast,
    get_origin,
)

from pydantic import BaseModel, ConfigDict, ValidationError, create_model
from tenacity import AsyncRetrying, RetryError, Retrying, stop_after_attempt

from ..partial import partial
from .calls import BaseCall
from .prompts import BasePrompt, BasePromptT
from .tools import BaseTool, BaseType
from .types import BaseCallParams, BaseConfig, BaseToolStream

with suppress(ImportError):
    import logfire

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
    configuration: ClassVar[BaseConfig] = BaseConfig(llm_ops=[])

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

    @classmethod
    def from_prompt(
        cls,
        prompt_type: type[BasePromptT],
        call_params: BaseCallParams,
        *,
        extract_schema: Optional[ExtractedType] = None,
    ) -> type[BasePromptT]:
        """Returns an extractor_type generated dynamically from this base extractor.

        Args:
            prompt_type: The prompt class to use for the extractor. Properties and class
                variables of this class will be used to create the new extractor class.
                Must be a class that can be instantiated.
            call_params: The call params to use for the extractor.
            extract_schema: The extract schema to use for the extractor. If none, the
                extractor will use the class' extract_schema.

        Returns:
            A new extractor class with new extractor type.
        """

        fields: dict[str, Any] = {
            name: (field.annotation, field.default)
            for name, field in prompt_type.model_fields.items()
        }

        if extract_schema is not None:
            fields["extract_schema"] = (type[extract_schema], extract_schema)  # type: ignore
        else:
            extract_schema = fields["extract_schema"][1]

        class_vars = {
            name: value
            for name, value in prompt_type.__dict__.items()
            if name not in prompt_type.model_fields
        }
        new_extractor = create_model(
            prompt_type.__name__,
            __base__=cls[extract_schema],  # type: ignore
            **fields,
        )

        for var_name, var_value in class_vars.items():
            setattr(new_extractor, var_name, var_value)
        setattr(new_extractor, "call_params", call_params)

        return cast(type[BasePromptT], new_extractor)

    ############################## PRIVATE METHODS ###################################

    def _extract(
        self,
        call_type: Type[BaseCallT],
        tool_type: Type[BaseToolT],
        retries: Union[int, Retrying] = 0,
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

        def _extract_attempt(
            call_type: Type[BaseCallT],
            tool_type: Type[BaseToolT],
            error_messages: dict[str, Any],
            **kwargs: Any,
        ) -> ExtractedTypeT:
            kwargs, return_tool = self._setup(tool_type, kwargs)

            temp_call = self._generate_temp_call(call_type, error_messages)
            response = temp_call(
                **self.model_dump(exclude={"extract_schema"}),
            ).call(**kwargs)
            try:
                extracted_schema = self._extract_schema(
                    response.tool, self.extract_schema, return_tool, response=response
                )
                if extracted_schema is None:
                    raise AttributeError("No tool found in the completion.")
                return extracted_schema
            except (AttributeError, ValueError, ValidationError):
                raise

        if isinstance(retries, int):
            if retries > 0:
                retries = Retrying(stop=stop_after_attempt(retries))
            else:
                return _extract_attempt(call_type, tool_type, {}, **kwargs)
        try:
            error_messages: dict[str, Any] = {}
            for attempt in retries:
                with attempt:
                    try:
                        extraction = _extract_attempt(
                            call_type, tool_type, error_messages, **kwargs
                        )
                    except (AttributeError, ValueError, ValidationError) as e:
                        error_messages[str(e)] = None
                        if "logfire" in self.configuration.llm_ops:  # pragma: no cover
                            logfire.error(f"Retrying due to exception: {e}")
                        raise
        except RetryError as e:
            raise e
        return extraction

    async def _extract_async(
        self,
        call_type: Type[BaseCallT],
        tool_type: Type[BaseToolT],
        retries: Union[int, AsyncRetrying],
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

        async def _extract_attempt_async(
            call_type: Type[BaseCallT],
            tool_type: Type[BaseToolT],
            error_messages: dict[str, Any],
            **kwargs: Any,
        ) -> ExtractedTypeT:
            kwargs, return_tool = self._setup(tool_type, kwargs)

            temp_call = self._generate_temp_call(call_type, error_messages)

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
            except (AttributeError, ValueError, ValidationError):
                raise

        if isinstance(retries, int):
            if retries > 0:
                retries = AsyncRetrying(stop=stop_after_attempt(retries))
            else:
                return await _extract_attempt_async(call_type, tool_type, {}, **kwargs)
        try:
            error_messages: dict[str, Any] = {}
            async for attempt in retries:
                with attempt:
                    try:
                        extraction = await _extract_attempt_async(
                            call_type, tool_type, error_messages, **kwargs
                        )
                    except (AttributeError, ValueError, ValidationError) as e:
                        error_messages[str(e)] = None
                        if "logfire" in self.configuration.llm_ops:  # pragma: no cover
                            logfire.error(f"Retrying due to exception: {e}")
                        raise
        except RetryError as e:
            raise e
        return extraction

    def _stream(
        self,
        call_type: Type[BaseCallT],
        tool_type: Type[BaseToolT],
        tool_stream_type: Type[BaseToolStreamT],
        retries: Union[int, Retrying],
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

        def _stream_attempt(
            call_type: Type[BaseCallT],
            tool_type: Type[BaseToolT],
            tool_stream_type: Type[BaseToolStreamT],
            error_messages: dict[str, Any],
            **kwargs: Any,
        ) -> Generator[ExtractedTypeT, None, None]:
            kwargs, return_tool = self._setup(tool_type, kwargs)

            temp_call = self._generate_temp_call(call_type, error_messages)

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
            except (AttributeError, ValueError, ValidationError):
                raise

        if isinstance(retries, int):
            if retries > 0:
                retries = Retrying(stop=stop_after_attempt(retries))
            else:
                for partial_tool in _stream_attempt(
                    call_type,
                    tool_type,
                    tool_stream_type,
                    {},
                    **kwargs,
                ):
                    yield partial_tool
                return
        try:
            error_messages: dict[str, Any] = {}
            for attempt in retries:
                with attempt:
                    try:
                        for partial_tool in _stream_attempt(
                            call_type,
                            tool_type,
                            tool_stream_type,
                            error_messages,
                            **kwargs,
                        ):
                            yield partial_tool
                    except (AttributeError, ValueError, ValidationError) as e:
                        error_messages[str(e)] = None
                        if "logfire" in self.configuration.llm_ops:  # pragma: no cover
                            logfire.error(f"Retrying due to exception: {e}")
                        raise
        except RetryError as e:
            raise e

    async def _stream_async(
        self,
        call_type: Type[BaseCallT],
        tool_type: Type[BaseToolT],
        tool_stream_type: Type[BaseToolStreamT],
        retries: Union[int, AsyncRetrying],
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

        async def _stream_attempt_async(
            call_type: Type[BaseCallT],
            tool_type: Type[BaseToolT],
            tool_stream_type: Type[BaseToolStreamT],
            error_messages: dict[str, Any],
            **kwargs: Any,
        ) -> AsyncGenerator[ExtractedTypeT, None]:
            kwargs, return_tool = self._setup(tool_type, kwargs)

            temp_call = self._generate_temp_call(call_type, error_messages)

            stream = temp_call(
                **self.model_dump(exclude={"extract_schema"})
            ).stream_async(**kwargs)
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
            except (AttributeError, ValueError, ValidationError):
                raise

        if isinstance(retries, int):
            if retries > 0:
                retries = AsyncRetrying(stop=stop_after_attempt(retries))
            else:
                async for partial_tool in _stream_attempt_async(
                    call_type, tool_type, tool_stream_type, {}, **kwargs
                ):
                    yield partial_tool
                return
        try:
            error_messages: dict[str, Any] = {}
            async for attempt in retries:
                with attempt:
                    try:
                        async for partial_tool in _stream_attempt_async(
                            call_type,
                            tool_type,
                            tool_stream_type,
                            error_messages,
                            **kwargs,
                        ):
                            yield partial_tool
                    except (AttributeError, ValueError, ValidationError) as e:
                        error_messages[str(e)] = None
                        if "logfire" in self.configuration.llm_ops:  # pragma: no cover
                            logfire.error(f"Retrying due to exception: {e}")
                        raise
        except RetryError as e:
            raise e

    def _generate_temp_call(
        self, call_type: Type[BaseCallT], error_messages: dict[str, Any]
    ) -> Type[BaseCallT]:
        """Returns a `TempCall` generated using the extractors definition."""
        _prompt_template = self.prompt_template
        if error_messages:
            formatted_error_messages = [
                "- " + element for element in error_messages.keys()
            ]
            error_messages_list = "\n".join(formatted_error_messages)
            _prompt_template = (
                f"{_prompt_template}\n"
                "Errors found:\n\n"
                f"{error_messages_list}\n\n"
                "Please fix the errors and try again."
            )

        class TempCall(call_type):  # type: ignore
            prompt_template = _prompt_template

            base_url = self.base_url
            api_key = self.api_key
            call_params = self.call_params
            configuration = self.configuration

            model_config = ConfigDict(extra="allow")

        properties = getmembers(self)
        for name, value in properties:
            if not hasattr(TempCall, name) or (
                name == "messages" and "messages" in self.__class__.__dict__
            ):
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


BaseExtractorT = TypeVar("BaseExtractorT", bound=BaseExtractor)
