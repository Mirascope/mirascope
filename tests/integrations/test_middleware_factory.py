from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from mirascope.core.base import BaseCallResponse
from mirascope.core.base.stream import (
    BaseStream,
)
from mirascope.core.base.structured_stream import BaseStructuredStream
from mirascope.core.base.types import CostMetadata
from mirascope.core.bedrock import AssistantMessageTypeDef
from mirascope.integrations._middleware_factory import (
    default_context_manager,
    middleware_factory,
)


def test_default_context_manager() -> None:
    with default_context_manager(lambda x: x) as result:
        assert result is None


def test_default_context_manager_async() -> None:
    async def async_fn(x):
        return x  # pragma: no cover

    with default_context_manager(async_fn) as result:
        assert result is None


def test_middleware_factory_call_response_sync() -> None:
    class MyCallResponse(BaseCallResponse):
        @property
        def content(self) -> str:
            return "content"

    patch.multiple(MyCallResponse, __abstractmethods__=set()).start()
    call_response = MyCallResponse(
        metadata={},
        response="",
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )  # type: ignore

    def sync_fn() -> MyCallResponse:
        return call_response

    def handle_call_response(result, fn, context) -> None:
        assert isinstance(result, BaseCallResponse)

    decorate = middleware_factory(handle_call_response=handle_call_response)(sync_fn)
    result = decorate()
    assert result.content == call_response.content


@pytest.mark.asyncio
async def test_middleware_factory_call_response_async() -> None:
    class MyCallResponse(BaseCallResponse):
        @property
        def content(self) -> str:
            return "content"

    patch.multiple(MyCallResponse, __abstractmethods__=set()).start()
    call_response = MyCallResponse(
        metadata={},
        response="",
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )  # type: ignore

    async def async_fn() -> MyCallResponse:
        return call_response

    async def handle_call_response_async(result, fn, context) -> None:
        assert isinstance(result, BaseCallResponse)

    decorate = middleware_factory(
        handle_call_response_async=handle_call_response_async
    )(async_fn)
    result = await decorate()
    assert result.content == call_response.content


def test_middleware_factory_stream_sync() -> None:
    patch.multiple(BaseStream, __abstractmethods__=set()).start()

    mock_chunk = MagicMock()
    mock_chunk.content = "content"
    mock_chunk.input_tokens = 1
    mock_chunk.output_tokens = 2
    mock_chunk.model = "updated_model"

    class MyStream(BaseStream):
        @property
        def cost(self) -> int:
            return 10

    # Usage
    stream_chunks = [(mock_chunk, None)]
    my_stream = MyStream(
        stream=(t for t in stream_chunks),
        metadata={},
        tool_types=[],
        call_response_type=MagicMock,
        model="model",
        prompt_template="prompt_template",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
    )  # type: ignore

    def sync_fn() -> BaseStream:
        return my_stream

    def handle_stream(result, fn, context) -> None:
        assert isinstance(result, BaseStream)

    decorate = middleware_factory(handle_stream=handle_stream)(sync_fn)
    result = decorate()
    result_chunks = []
    for chunk, _ in result:
        result_chunks.append(chunk.content)
    for result_chunk, stream_chunk in zip(result_chunks, stream_chunks, strict=False):
        assert result_chunk == stream_chunk[0].content
    assert my_stream.cost == result.cost


@pytest.mark.asyncio
async def test_middleware_factory_stream_async() -> None:
    patch.multiple(BaseStream, __abstractmethods__=set()).start()

    mock_chunk = MagicMock()
    mock_chunk.content = "content"
    mock_chunk.input_tokens = 1
    mock_chunk.output_tokens = 2
    mock_chunk.model = "updated_model"

    class MyStream(BaseStream):
        @property
        def cost(self) -> int:
            return 10

    # Usage
    stream_chunks = [(mock_chunk, None)]
    my_stream = MyStream(
        stream=(t for t in stream_chunks),
        metadata={},
        tool_types=[],
        call_response_type=MagicMock,
        model="model",
        prompt_template="prompt_template",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
    )  # type: ignore

    async def generator():
        yield mock_chunk, None

    my_stream.stream = generator()

    async def async_fn() -> BaseStream:
        return my_stream

    async def handle_stream_async(result, fn, context) -> None:
        assert isinstance(result, BaseStream)

    decorate = middleware_factory(handle_stream_async=handle_stream_async)(async_fn)
    result = await decorate()
    result_chunks = []
    async for chunk, _ in result:
        result_chunks.append(chunk.content)
    for result_chunk, stream_chunk in zip(result_chunks, stream_chunks, strict=False):
        assert result_chunk == stream_chunk[0].content
    assert my_stream.cost == result.cost
    assert my_stream.cost_metadata == result.cost_metadata


def test_middleware_factory_base_model_sync() -> None:
    class Foo(BaseModel):
        bar: str
        baz: int

    def sync_fn() -> Foo:
        return Foo(bar="bar", baz=1)

    def handle_response_model(result, fn, context) -> None:
        assert isinstance(result, BaseModel)

    decorate = middleware_factory(handle_response_model=handle_response_model)(sync_fn)
    result = decorate()
    assert result.model_dump() == sync_fn().model_dump()


@pytest.mark.asyncio
async def test_middleware_factory_base_model_async() -> None:
    class Foo(BaseModel):
        bar: str
        baz: int

    async def async_fn() -> Foo:
        return Foo(bar="bar", baz=1)

    async def handle_response_model_async(result, fn, context) -> None:
        assert isinstance(result, BaseModel)

    decorate = middleware_factory(
        handle_response_model_async=handle_response_model_async
    )(async_fn)
    result = await decorate()
    async_fn_result = await async_fn()
    assert result.model_dump() == async_fn_result.model_dump()


def test_middleware_factory_structured_stream() -> None:
    patch.multiple(BaseStream, __abstractmethods__=set()).start()

    class Foo(BaseModel):
        bar: str
        baz: int

    mock_chunk = MagicMock()
    my_foo = Foo(bar="bar", baz=1)
    mock_chunk.content = my_foo.model_dump_json()
    mock_chunk.input_tokens = 1
    mock_chunk.output_tokens = 2
    mock_chunk.model = "updated_model"

    base_stream = MagicMock()
    base_stream.__iter__.return_value = (t for t in [(mock_chunk, None)])
    my_structured_stream = BaseStructuredStream(
        stream=base_stream, response_model=Foo, fields_from_call_args={}
    )

    def sync_fn() -> BaseStructuredStream:
        return my_structured_stream

    def handle_structured_stream(result, fn, context) -> None:
        assert isinstance(result, BaseStructuredStream)

    decorate = middleware_factory(handle_structured_stream=handle_structured_stream)(
        sync_fn
    )
    for chunk in decorate():
        assert chunk.model_dump() == my_foo.model_dump()


@pytest.mark.asyncio
async def test_middleware_factory_structured_stream_async() -> None:
    patch.multiple(BaseStream, __abstractmethods__=set()).start()

    class Foo(BaseModel):
        bar: str
        baz: int

    mock_chunk = MagicMock()
    my_foo = Foo(bar="bar", baz=1)
    mock_chunk.content = my_foo.model_dump_json()
    mock_chunk.input_tokens = 1
    mock_chunk.output_tokens = 2
    mock_chunk.model = "updated_model"

    base_stream = MagicMock()

    async def generator(self):
        yield mock_chunk, None

    base_stream.__aiter__ = generator
    my_structured_stream = BaseStructuredStream(
        stream=base_stream, response_model=Foo, fields_from_call_args={}
    )

    async def async_fn() -> BaseStructuredStream:
        return my_structured_stream

    async def handle_structured_stream_async(result, fn, context) -> None:
        assert isinstance(result, BaseStructuredStream)

    decorate = middleware_factory(
        handle_structured_stream_async=handle_structured_stream_async
    )(async_fn)
    async for chunk in await decorate():
        assert chunk.model_dump() == my_foo.model_dump()


def test_middleware_factory_handle_error_sync() -> None:
    def sync_fn():
        raise ValueError("An error occurred")

    def handle_error(e, fn, context):
        assert isinstance(e, ValueError)
        return "Handled Error"

    decorate = middleware_factory(handle_error=handle_error)(sync_fn)
    result = decorate()
    assert result == "Handled Error"


@pytest.mark.asyncio
async def test_middleware_factory_handle_error_async() -> None:
    async def async_fn():
        raise ValueError("An error occurred")

    async def handle_error_async(e, fn, context):
        assert isinstance(e, ValueError)
        return "Handled Error"

    decorate = middleware_factory(handle_error_async=handle_error_async)(async_fn)
    result = await decorate()
    assert result == "Handled Error"


def test_middleware_factory_handle_error_sync_exception() -> None:
    def sync_fn():
        raise ValueError("An error occurred")

    def handle_error(e, fn, context):
        raise RuntimeError("New error in handle_error")

    decorate = middleware_factory(handle_error=handle_error)(sync_fn)
    with pytest.raises(RuntimeError, match="New error in handle_error"):
        decorate()


@pytest.mark.asyncio
async def test_middleware_factory_handle_error_async_exception() -> None:
    async def async_fn():
        raise ValueError("An error occurred")

    async def handle_error_async(e, fn, context):
        raise RuntimeError("New error in handle_error_async")

    decorate = middleware_factory(handle_error_async=handle_error_async)(async_fn)
    with pytest.raises(RuntimeError, match="New error in handle_error_async"):
        await decorate()


def test_middleware_factory_handle_error_no_handler() -> None:
    def sync_fn():
        raise ValueError("An error occurred")

    decorate = middleware_factory()(sync_fn)
    with pytest.raises(ValueError, match="An error occurred"):
        decorate()


@pytest.mark.asyncio
async def test_middleware_factory_handle_error_async_no_handler() -> None:
    async def async_fn():
        raise ValueError("An error occurred")

    decorate = middleware_factory()(async_fn)
    with pytest.raises(ValueError, match="An error occurred"):
        await decorate()


def test_middleware_factory_stream_sync_exception() -> None:
    patch.multiple(BaseStream, __abstractmethods__=set()).start()

    def sync_fn() -> BaseStream:
        def iterator():
            yield "chunk1", None
            raise ValueError("Stream error")

        class MyStream(BaseStream):
            def _construct_message_param(
                self, tool_calls: list[Any] | None = None, content: str | None = None
            ) -> AssistantMessageTypeDef: ...  # pyright ignore [reportReturnType]

            def construct_call_response(
                self,
            ) -> BaseCallResponse: ...  # pyright ignore [reportReturnType]

            @property
            def cost(self) -> int:
                return 10  # pragma: no cover

            def __iter__(self):
                return iterator()

            @property
            def cost_metadata(self) -> CostMetadata: ...

        return MyStream(
            stream=None,  # pyright: ignore [reportArgumentType]
            metadata={},
            tool_types=[],
            call_response_type=MagicMock,
            model="model",
            prompt_template="prompt_template",
            fn_args={},
            dynamic_config=None,
            messages=[],
            call_params={},
            call_kwargs={},
        )

    handle_error_called = False

    def handle_error(e, fn, context):
        nonlocal handle_error_called
        handle_error_called = True
        assert isinstance(e, ValueError)
        return "Handled Stream Error"

    decorate = middleware_factory(handle_error=handle_error)(sync_fn)
    result = decorate()
    collected_chunks = []
    for chunk, _ in result:
        collected_chunks.append(chunk)
    assert collected_chunks == ["chunk1"]
    assert handle_error_called


@pytest.mark.asyncio
async def test_middleware_factory_stream_async_exception() -> None:
    patch.multiple(BaseStream, __abstractmethods__=set()).start()

    async def async_fn() -> BaseStream:
        async def iterator():
            yield "chunk1", None
            raise ValueError("Stream error")

        class MyStream(BaseStream):
            def construct_call_response(self) -> BaseCallResponse: ...

            def _construct_message_param(
                self, tool_calls: list[Any] | None = None, content: str | None = None
            ) -> AssistantMessageTypeDef: ...

            @property
            def cost(self) -> int:
                return 10  # pragma: no cover

            def __aiter__(self):
                return iterator()

            @property
            def cost_metadata(self) -> CostMetadata: ...

        return MyStream(
            stream=None,  # pyright: ignore [reportArgumentType]
            metadata={},
            tool_types=[],
            call_response_type=MagicMock,
            model="model",
            prompt_template="prompt_template",
            fn_args={},
            dynamic_config=None,
            messages=[],
            call_params={},
            call_kwargs={},
        )

    handle_error_async_called = False

    async def handle_error_async(e, fn, context):
        nonlocal handle_error_async_called
        handle_error_async_called = True
        assert isinstance(e, ValueError)
        return "Handled Stream Error"

    decorate = middleware_factory(handle_error_async=handle_error_async)(async_fn)
    result = await decorate()
    collected_chunks = []
    async for chunk, _ in result:
        collected_chunks.append(chunk)
    assert collected_chunks == ["chunk1"]
    assert handle_error_async_called


def test_middleware_factory_stream_sync_exception_no_handler() -> None:
    patch.multiple(BaseStream, __abstractmethods__=set()).start()

    def sync_fn() -> BaseStream:
        def iterator():
            yield "chunk1", None
            raise ValueError("Stream error")

        class MyStream(BaseStream):
            def _construct_message_param(
                self, tool_calls: list[Any] | None = None, content: str | None = None
            ) -> AssistantMessageTypeDef: ...

            def construct_call_response(self) -> BaseCallResponse: ...

            @property
            def cost(self) -> int:
                return 10  # pragma: no cover

            def __iter__(self):
                return iterator()

            @property
            def cost_metadata(self) -> CostMetadata: ...

        return MyStream(
            stream=None,  # pyright: ignore [reportArgumentType]
            metadata={},
            tool_types=[],
            call_response_type=MagicMock,
            model="model",
            prompt_template="prompt_template",
            fn_args={},
            dynamic_config=None,
            messages=[],
            call_params={},
            call_kwargs={},
        )

    decorate = middleware_factory()(sync_fn)
    result = decorate()
    with pytest.raises(ValueError, match="Stream error"):
        for chunk, _ in result:  # noqa: B007
            pass


@pytest.mark.asyncio
async def test_middleware_factory_stream_async_exception_no_handler() -> None:
    patch.multiple(BaseStream, __abstractmethods__=set()).start()

    async def async_fn() -> BaseStream:
        async def iterator():
            yield "chunk1", None
            raise ValueError("Stream error")

        class MyStream(BaseStream):
            def _construct_message_param(
                self, tool_calls: list[Any] | None = None, content: str | None = None
            ) -> AssistantMessageTypeDef: ...

            def construct_call_response(self) -> BaseCallResponse: ...

            @property
            def cost(self) -> int:
                return 10  # pragma: no cover

            def __aiter__(self):
                return iterator()

            @property
            def cost_metadata(self) -> CostMetadata: ...

        return MyStream(
            stream=None,  # pyright: ignore [reportArgumentType]
            metadata={},
            tool_types=[],
            call_response_type=MagicMock,
            model="model",
            prompt_template="prompt_template",
            fn_args={},
            dynamic_config=None,
            messages=[],
            call_params={},
            call_kwargs={},
        )

    decorate = middleware_factory()(async_fn)
    result = await decorate()
    with pytest.raises(ValueError, match="Stream error"):
        async for chunk, _ in result:  # noqa: B007
            pass


def test_middleware_factory_handle_error_sync_in_handle_call_response() -> None:
    class MyCallResponse(BaseCallResponse):
        @property
        def content(self) -> str:
            return "content"  # pragma: no cover

    patch.multiple(MyCallResponse, __abstractmethods__=set()).start()
    call_response = MyCallResponse(
        metadata={},
        response="",
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )  # type: ignore

    def sync_fn() -> MyCallResponse:
        return call_response

    def handle_call_response(result, fn, context) -> None:
        raise RuntimeError("Error in handle_call_response")

    decorate = middleware_factory(handle_call_response=handle_call_response)(sync_fn)
    with pytest.raises(RuntimeError, match="Error in handle_call_response"):
        decorate()


@pytest.mark.asyncio
async def test_middleware_factory_handle_error_async_in_handle_call_response_async() -> (
    None
):
    class MyCallResponse(BaseCallResponse):
        @property
        def content(self) -> str:
            return "content"  # pragma: no cover

    patch.multiple(MyCallResponse, __abstractmethods__=set()).start()
    call_response = MyCallResponse(
        metadata={},
        response="",
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )  # type: ignore

    async def async_fn() -> MyCallResponse:
        return call_response

    async def handle_call_response_async(result, fn, context) -> None:
        raise RuntimeError("Error in handle_call_response_async")

    decorate = middleware_factory(
        handle_call_response_async=handle_call_response_async
    )(async_fn)
    with pytest.raises(RuntimeError, match="Error in handle_call_response_async"):
        await decorate()


def test_middleware_factory_handle_error_sync_in_custom_context_manager() -> None:
    def sync_fn():
        return "result"  # pragma: no cover

    def custom_context_manager(fn):
        class CustomContextManager:
            def __enter__(self):
                raise RuntimeError("Error in custom_context_manager")

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass  # pragma: no cover

        return CustomContextManager()

    decorate = middleware_factory(custom_context_manager=custom_context_manager)(
        sync_fn
    )
    with pytest.raises(RuntimeError, match="Error in custom_context_manager"):
        decorate()


@pytest.mark.asyncio
async def test_middleware_factory_handle_error_async_in_custom_context_manager() -> (
    None
):
    async def async_fn():
        return "result"  # pragma: no cover

    def custom_context_manager(fn):
        class CustomContextManager:
            def __enter__(self):
                raise RuntimeError("Error in custom_context_manager")

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass  # pragma: no cover

        return CustomContextManager()

    decorate = middleware_factory(custom_context_manager=custom_context_manager)(
        async_fn
    )
    with pytest.raises(RuntimeError, match="Error in custom_context_manager"):
        await decorate()


def test_middleware_factory_no_handle_functions() -> None:
    def sync_fn():
        return "result"

    decorate = middleware_factory()(sync_fn)
    result = decorate()
    assert result == "result"


@pytest.mark.asyncio
async def test_middleware_factory_no_handle_functions_async() -> None:
    async def async_fn():
        return "result"

    decorate = middleware_factory()(async_fn)
    result = await decorate()
    assert result == "result"


def test_middleware_factory_handle_error_in_handle_error() -> None:
    def sync_fn():
        raise ValueError("An error occurred")

    def handle_error(e, fn, context):
        raise RuntimeError("Error in handle_error")

    decorate = middleware_factory(handle_error=handle_error)(sync_fn)
    with pytest.raises(RuntimeError, match="Error in handle_error"):
        decorate()


@pytest.mark.asyncio
async def test_middleware_factory_handle_error_async_in_handle_error_async() -> None:
    async def async_fn():
        raise ValueError("An error occurred")

    async def handle_error_async(e, fn, context):
        raise RuntimeError("Error in handle_error_async")

    decorate = middleware_factory(handle_error_async=handle_error_async)(async_fn)
    with pytest.raises(RuntimeError, match="Error in handle_error_async"):
        await decorate()


@pytest.mark.asyncio
async def test_middleware_factory_stream_async_with_error() -> None:
    """Test error handling in async stream."""
    patch.multiple(BaseStream, __abstractmethods__=set()).start()

    class StreamError(Exception):
        pass

    async def async_fn() -> BaseStream:
        async def iterator():
            yield "chunk1", None
            raise StreamError("Stream error")

        class MyStream(BaseStream):
            def _construct_message_param(
                self, tool_calls: list[Any] | None = None, content: str | None = None
            ) -> AssistantMessageTypeDef: ...

            def construct_call_response(self) -> BaseCallResponse: ...

            @property
            def cost(self) -> int:
                return 10  # pragma: no cover

            def __aiter__(self):
                return iterator()

            @property
            def cost_metadata(self) -> CostMetadata: ...

        return MyStream(
            stream=None,  # pyright: ignore [reportArgumentType]
            metadata={},
            tool_types=[],
            call_response_type=MagicMock,
            model="model",
            prompt_template="prompt_template",
            fn_args={},
            dynamic_config=None,
            messages=[],
            call_params={},
            call_kwargs={},
        )

    error_handled = False

    async def handle_error_async(e, fn, context):
        nonlocal error_handled
        error_handled = True
        assert isinstance(e, StreamError)
        return "Error Handled"

    decorate = middleware_factory(handle_error_async=handle_error_async)(async_fn)
    result = await decorate()
    chunks = []
    async for chunk, _ in result:
        chunks.append(chunk)

    assert chunks == ["chunk1"]
    assert error_handled


@pytest.mark.asyncio
async def test_middleware_factory_stream_async_error_handling_fails() -> None:
    """Test when error handler itself raises an exception."""
    patch.multiple(BaseStream, __abstractmethods__=set()).start()

    class StreamError(Exception):
        pass

    async def async_fn() -> BaseStream:
        async def iterator():
            yield "chunk1", None
            raise StreamError("Stream error")

        class MyStream(BaseStream):
            def _construct_message_param(
                self, tool_calls: list[Any] | None = None, content: str | None = None
            ) -> AssistantMessageTypeDef: ...

            def construct_call_response(self) -> BaseCallResponse: ...

            @property
            def cost(self) -> int:
                return 10  # pragma: no cover

            def __aiter__(self):
                return iterator()

            @property
            def cost_metadata(self) -> CostMetadata: ...

        return MyStream(
            stream=None,  # pyright: ignore [reportArgumentType]
            metadata={},
            tool_types=[],
            call_response_type=MagicMock,
            model="model",
            prompt_template="prompt_template",
            fn_args={},
            dynamic_config=None,
            messages=[],
            call_params={},
            call_kwargs={},
        )

    async def handle_error_async(e, fn, context):
        raise RuntimeError("Error handler failed")

    decorate = middleware_factory(handle_error_async=handle_error_async)(async_fn)
    result = await decorate()

    with pytest.raises(RuntimeError, match="Error handler failed"):
        async for _ in result:
            pass


def test_middleware_factory_structured_stream_with_error() -> None:
    """Test error handling in structured stream."""
    patch.multiple(BaseStream, __abstractmethods__=set()).start()

    class StreamError(Exception):
        pass

    class Foo(BaseModel):
        bar: str
        baz: int

    def sync_fn() -> BaseStructuredStream:
        def iterator():
            yield "chunk1"
            raise StreamError("Stream error")

        class MyStructuredStream(BaseStructuredStream):
            def __iter__(self):
                return iterator()

        base_stream = MagicMock()
        base_stream.__iter__.return_value = iterator()
        return MyStructuredStream(
            stream=base_stream, response_model=Foo, fields_from_call_args={}
        )

    error_handled = False

    def handle_error(e, fn, context):
        nonlocal error_handled
        error_handled = True
        assert isinstance(e, StreamError)
        return "Error Handled"

    decorate = middleware_factory(handle_error=handle_error)(sync_fn)
    result = decorate()
    chunks = []
    for chunk in result:
        chunks.append(chunk)

    assert chunks == ["chunk1"]
    assert error_handled


@pytest.mark.asyncio
async def test_middleware_factory_structured_stream_async_with_error() -> None:
    """Test error handling in async structured stream."""
    patch.multiple(BaseStream, __abstractmethods__=set()).start()

    class StreamError(Exception):
        pass

    class Foo(BaseModel):
        bar: str
        baz: int

    async def async_fn() -> BaseStructuredStream:
        async def iterator():
            yield "chunk1"
            raise StreamError("Stream error")

        class MyStructuredStream(BaseStructuredStream):
            def __aiter__(self):
                return iterator()

        base_stream = MagicMock()
        base_stream.__aiter__ = iterator
        return MyStructuredStream(
            stream=base_stream, response_model=Foo, fields_from_call_args={}
        )

    error_handled = False

    async def handle_error_async(e, fn, context):
        nonlocal error_handled
        error_handled = True
        assert isinstance(e, StreamError)
        return "Error Handled"

    decorate = middleware_factory(handle_error_async=handle_error_async)(async_fn)
    result = await decorate()
    chunks = []
    async for chunk in result:
        chunks.append(chunk)

    assert chunks == ["chunk1"]
    assert error_handled


def test_stream_without_error_handler() -> None:
    """Test stream behavior when no error handler is provided."""
    patch.multiple(BaseStream, __abstractmethods__=set()).start()

    class StreamError(Exception):
        pass

    def sync_fn() -> BaseStream:
        def iterator():
            yield "chunk1", None
            raise StreamError("Stream error")

        class MyStream(BaseStream):
            def _construct_message_param(
                self, tool_calls: list[Any] | None = None, content: str | None = None
            ) -> AssistantMessageTypeDef: ...

            def construct_call_response(self) -> BaseCallResponse: ...

            @property
            def cost(self) -> int:
                return 10  # pragma: no cover

            def __iter__(self):
                return iterator()

            @property
            def cost_metadata(self) -> CostMetadata: ...

        return MyStream(
            stream=None,  # pyright: ignore [reportArgumentType]
            metadata={},
            tool_types=[],
            call_response_type=MagicMock,
            model="model",
            prompt_template="prompt_template",
            fn_args={},
            dynamic_config=None,
            messages=[],
            call_params={},
            call_kwargs={},
        )

    decorate = middleware_factory()(sync_fn)
    result = decorate()
    chunks = []

    with pytest.raises(StreamError, match="Stream error"):
        for chunk, _ in result:
            chunks.append(chunk)

    assert chunks == ["chunk1"]


def test_structured_stream_without_error_handler() -> None:
    """Test structured stream behavior when no error handler is provided."""
    patch.multiple(BaseStream, __abstractmethods__=set()).start()

    class StreamError(Exception):
        pass

    class Foo(BaseModel):
        bar: str
        baz: int

    def sync_fn() -> BaseStructuredStream:
        def iterator():
            yield "chunk1"
            raise StreamError("Stream error")

        class MyStructuredStream(BaseStructuredStream):
            def __iter__(self):
                return iterator()

        base_stream = MagicMock()
        base_stream.__iter__.return_value = iterator()
        return MyStructuredStream(
            stream=base_stream, response_model=Foo, fields_from_call_args={}
        )

    decorate = middleware_factory()(sync_fn)
    result = decorate()
    chunks = []

    with pytest.raises(StreamError, match="Stream error"):
        for chunk in result:
            chunks.append(chunk)

    assert chunks == ["chunk1"]


@pytest.mark.asyncio
async def test_middleware_factory_stream_error_handler_exception_async() -> None:
    """Test when stream error handler raises an exception in async stream."""
    patch.multiple(BaseStream, __abstractmethods__=set()).start()

    class StreamError(Exception):
        pass

    class ErrorHandlerError(Exception):
        pass

    handled = False

    async def async_fn() -> BaseStream:
        async def iterator():
            yield "chunk1", None
            raise StreamError("Stream error")

        class MyStream(BaseStream):
            def _construct_message_param(
                self, tool_calls: list[Any] | None = None, content: str | None = None
            ) -> AssistantMessageTypeDef: ...

            def construct_call_response(self) -> BaseCallResponse: ...

            @property
            def cost(self) -> int:
                return 10  # pragma: no cover

            def __aiter__(self):
                return iterator()

            @property
            def cost_metadata(self) -> CostMetadata: ...

        return MyStream(
            stream=None,  # pyright: ignore [reportArgumentType]
            metadata={},
            tool_types=[],
            call_response_type=MagicMock,
            model="model",
            prompt_template="prompt_template",
            fn_args={},
            dynamic_config=None,
            messages=[],
            call_params={},
            call_kwargs={},
        )

    async def handle_error_async(e, fn, context):
        nonlocal handled
        handled = True
        assert isinstance(e, StreamError)
        raise ErrorHandlerError("Error handler failed")

    decorate = middleware_factory(handle_error_async=handle_error_async)(async_fn)
    result = await decorate()
    chunks = []

    with pytest.raises(ErrorHandlerError, match="Error handler failed"):
        async for chunk, _ in result:
            chunks.append(chunk)

    assert chunks == ["chunk1"]
    assert handled


@pytest.mark.asyncio
async def test_middleware_factory_structured_stream_error_handler_exception_async() -> (
    None
):
    """Test when structured stream error handler raises an exception in async stream."""
    patch.multiple(BaseStream, __abstractmethods__=set()).start()

    class StreamError(Exception):
        pass

    class ErrorHandlerError(Exception):
        pass

    class Foo(BaseModel):
        bar: str
        baz: int

    handled = False

    async def async_fn() -> BaseStructuredStream:
        async def iterator():
            yield "chunk1"
            raise StreamError("Stream error")

        class MyStructuredStream(BaseStructuredStream):
            def __aiter__(self):
                return iterator()

        base_stream = MagicMock()
        base_stream.__aiter__ = iterator
        return MyStructuredStream(
            stream=base_stream, response_model=Foo, fields_from_call_args={}
        )

    async def handle_error_async(e, fn, context):
        nonlocal handled
        handled = True
        assert isinstance(e, StreamError)
        raise ErrorHandlerError("Error handler failed")

    decorate = middleware_factory(handle_error_async=handle_error_async)(async_fn)
    result = await decorate()
    chunks = []

    with pytest.raises(ErrorHandlerError, match="Error handler failed"):
        async for chunk in result:
            chunks.append(chunk)

    assert chunks == ["chunk1"]
    assert handled


def test_middleware_factory_stream_error_handler_exception() -> None:
    """Test when stream error handler raises an exception in sync stream."""
    patch.multiple(BaseStream, __abstractmethods__=set()).start()

    class StreamError(Exception):
        pass

    class ErrorHandlerError(Exception):
        pass

    handled = False

    def sync_fn() -> BaseStream:
        def iterator():
            yield "chunk1", None
            raise StreamError("Stream error")

        class MyStream(BaseStream):
            def _construct_message_param(
                self, tool_calls: list[Any] | None = None, content: str | None = None
            ) -> AssistantMessageTypeDef: ...

            def construct_call_response(self) -> BaseCallResponse: ...

            @property
            def cost(self) -> int:
                return 10  # pragma: no cover

            def __iter__(self):
                return iterator()

            @property
            def cost_metadata(self) -> CostMetadata: ...

        return MyStream(
            stream=None,  # pyright: ignore [reportArgumentType]
            metadata={},
            tool_types=[],
            call_response_type=MagicMock,
            model="model",
            prompt_template="prompt_template",
            fn_args={},
            dynamic_config=None,
            messages=[],
            call_params={},
            call_kwargs={},
        )

    def handle_error(e, fn, context):
        nonlocal handled
        handled = True
        assert isinstance(e, StreamError)
        raise ErrorHandlerError("Error handler failed")

    decorate = middleware_factory(handle_error=handle_error)(sync_fn)
    result = decorate()
    chunks = []

    with pytest.raises(ErrorHandlerError, match="Error handler failed"):
        for chunk, _ in result:
            chunks.append(chunk)

    assert chunks == ["chunk1"]
    assert handled


def test_middleware_factory_structured_stream_error_handler_exception() -> None:
    """Test when structured stream error handler raises an exception in sync stream."""
    patch.multiple(BaseStream, __abstractmethods__=set()).start()

    class StreamError(Exception):
        pass

    class ErrorHandlerError(Exception):
        pass

    class Foo(BaseModel):
        bar: str
        baz: int

    handled = False

    def sync_fn() -> BaseStructuredStream:
        def iterator():
            yield "chunk1"
            raise StreamError("Stream error")

        class MyStructuredStream(BaseStructuredStream):
            def __iter__(self):
                return iterator()

        base_stream = MagicMock()
        base_stream.__iter__.return_value = iterator()
        return MyStructuredStream(
            stream=base_stream, response_model=Foo, fields_from_call_args={}
        )

    def handle_error(e, fn, context):
        nonlocal handled
        handled = True
        assert isinstance(e, StreamError)
        raise ErrorHandlerError("Error handler failed")

    decorate = middleware_factory(handle_error=handle_error)(sync_fn)
    result = decorate()
    chunks = []

    with pytest.raises(ErrorHandlerError, match="Error handler failed"):
        for chunk in result:
            chunks.append(chunk)

    assert chunks == ["chunk1"]
    assert handled


def test_middleware_factory_structured_stream_error_no_handler() -> None:
    """Test when structured stream raises an error and no handler is provided."""
    patch.multiple(BaseStream, __abstractmethods__=set()).start()

    class StreamError(Exception):
        pass

    class Foo(BaseModel):
        bar: str
        baz: int

    def sync_fn() -> BaseStructuredStream:
        def iterator():
            yield "chunk1"
            raise StreamError("Stream error")

        class MyStructuredStream(BaseStructuredStream):
            def __iter__(self):
                return iterator()

        base_stream = MagicMock()
        base_stream.__iter__.return_value = iterator()
        return MyStructuredStream(
            stream=base_stream, response_model=Foo, fields_from_call_args={}
        )

    decorate = middleware_factory()(sync_fn)
    result = decorate()
    chunks = []

    with pytest.raises(StreamError, match="Stream error"):
        for chunk in result:
            chunks.append(chunk)

    assert chunks == ["chunk1"]


@pytest.mark.asyncio
async def test_middleware_factory_structured_stream_error_no_handler_async() -> None:
    """Test when async structured stream raises an error and no handler is provided."""
    patch.multiple(BaseStream, __abstractmethods__=set()).start()

    class StreamError(Exception):
        pass

    class Foo(BaseModel):
        bar: str
        baz: int

    async def async_fn() -> BaseStructuredStream:
        async def iterator():
            yield "chunk1"
            raise StreamError("Stream error")

        class MyStructuredStream(BaseStructuredStream):
            def __aiter__(self):
                return iterator()

        base_stream = MagicMock()
        base_stream.__aiter__ = iterator
        return MyStructuredStream(
            stream=base_stream, response_model=Foo, fields_from_call_args={}
        )

    decorate = middleware_factory()(async_fn)
    result = await decorate()
    chunks = []

    with pytest.raises(StreamError, match="Stream error"):
        async for chunk in result:
            chunks.append(chunk)

    assert chunks == ["chunk1"]
