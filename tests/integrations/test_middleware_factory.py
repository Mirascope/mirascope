from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from mirascope.core.base import BaseCallResponse
from mirascope.core.base.stream import BaseStream
from mirascope.core.base.structured_stream import BaseStructuredStream
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
