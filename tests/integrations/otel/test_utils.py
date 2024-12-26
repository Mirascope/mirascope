import json
from functools import cached_property
from typing import cast
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel, Field

from mirascope.core.base.call_kwargs import BaseCallKwargs
from mirascope.core.base.call_response import BaseCallResponse
from mirascope.core.base.stream import BaseStream
from mirascope.core.base.structured_stream import BaseStructuredStream
from mirascope.core.base.tool import BaseTool
from mirascope.integrations.otel import _utils


class FormatBook(BaseTool):
    """Returns the title and author of a book nicely formatted."""

    title: str = Field(..., description="The title of the book.")
    author: str = Field(..., description="The author of the book in all caps.")

    def call(self) -> str:
        return f"{self.title} by {self.author}"  # pragma: no cover


class MyCallResponse(BaseCallResponse):
    @property
    def content(self) -> str:
        return "content"  # pragma: no cover

    @cached_property
    def tools(self) -> list[BaseTool]:
        return [
            FormatBook(title="The Name of the Wind", author="Rothfuss, Patrick")
        ]  # pragma: no cover


patch.multiple(MyCallResponse, __abstractmethods__=set()).start()
patch.multiple(BaseStream, __abstractmethods__=set()).start()


@patch("mirascope.integrations.otel._utils.get_tracer", new_callable=MagicMock)
def test_custom_context_manager(mock_get_tracer: MagicMock) -> None:
    """Tests the `custom_context_manager` function."""
    mock_fn = MagicMock(__name__="dummy_function")
    mock_span = MagicMock(name="MockSpan")
    mock_tracer = MagicMock()
    mock_tracer.start_as_current_span.return_value = mock_span
    mock_span.__enter__.return_value = mock_span
    mock_get_tracer.return_value = mock_tracer

    with _utils.custom_context_manager(mock_fn) as span:
        mock_get_tracer.assert_called_once_with("otel")
        assert span is mock_span
        mock_tracer.start_as_current_span.assert_called_once_with("dummy_function")


@patch("mirascope.integrations.otel._utils.get_tracer", new_callable=MagicMock)
@patch("mirascope.integrations.otel._utils.set_tracer_provider", new_callable=MagicMock)
@patch("mirascope.integrations.otel._utils.TracerProvider", new_callable=MagicMock)
@patch("mirascope.integrations.otel._utils.SimpleSpanProcessor", new_callable=MagicMock)
@patch("mirascope.integrations.otel._utils.ConsoleSpanExporter", new_callable=MagicMock)
def test_configure_no_processor(
    mock_console_span_exporter: MagicMock,
    mock_simple_span_processor: MagicMock,
    mock_tracer_provider: MagicMock,
    mock_set_tracer_provider: MagicMock,
    mock_get_tracer: MagicMock,
) -> None:
    """Tests the `configure` function with no processors."""
    mock_add_span_processor = MagicMock()
    mock_tracer_provider.return_value.add_span_processor = mock_add_span_processor
    _utils.configure(None)
    mock_tracer_provider.assert_called_once()
    mock_console_span_exporter.assert_called_once()
    mock_simple_span_processor.assert_called_once_with(
        mock_console_span_exporter.return_value
    )
    mock_add_span_processor.assert_called_once_with(
        mock_simple_span_processor.return_value
    )
    mock_set_tracer_provider.assert_called_once_with(mock_tracer_provider.return_value)
    mock_get_tracer.assert_called_once_with("otel")


@patch("mirascope.integrations.otel._utils.get_tracer", new_callable=MagicMock)
@patch("mirascope.integrations.otel._utils.set_tracer_provider", new_callable=MagicMock)
@patch("mirascope.integrations.otel._utils.TracerProvider", new_callable=MagicMock)
def test_configure_with_processors(
    mock_tracer_provider: MagicMock,
    mock_set_tracer_provider: MagicMock,
    mock_get_tracer: MagicMock,
) -> None:
    """Tests the `configure` function with processors."""
    processors: list = [MagicMock()]
    mock_add_span_processor = MagicMock()
    mock_tracer_provider.return_value.add_span_processor = mock_add_span_processor
    _utils.configure(processors)
    mock_tracer_provider.assert_called_once()
    mock_add_span_processor.assert_called_once_with(processors[0])
    mock_set_tracer_provider.assert_called_once_with(mock_tracer_provider.return_value)
    mock_get_tracer.assert_called_once_with("otel")


def test_get_call_response_attributes() -> None:
    """Tests the `_get_call_response_attributes` function."""
    call_response = MyCallResponse(
        metadata={"tags": {"version:0001"}},
        response="hello world",
        tool_types=[],
        prompt_template="Recommend a {genre} book for me to read.",
        fn_args={"genre": "nonfiction"},
        dynamic_config={"computed_fields": {"genre": "nonfiction"}},
        messages=[],
        call_params={"tool_choice": "required"},
        call_kwargs=cast(
            BaseCallKwargs,
            {
                "tool_choice": "required",
                "tools": [],
                "model": "gpt-4o",
                "messages": [],
            },
        ),
        user_message_param={
            "role": "user",
            "content": [
                {"type": "text", "text": "Recommend a nonfiction book for me to read."}
            ],
        },
        start_time=100,
        end_time=200,
    )  # type: ignore
    result = _utils._get_call_response_attributes(call_response)
    assert result["gen_ai.system"] == call_response.prompt_template
    assert result["gen_ai.request.model"] == call_response.call_kwargs.get("model")
    assert result["gen_ai.request.max_tokens"] == 0
    assert result["gen_ai.request.temperature"] == 0
    assert result["gen_ai.request.top_p"] == 0
    assert result["gen_ai.response.model"] == (
        call_response.model if call_response.model else ""
    )
    assert result["gen_ai.response.id"] == (
        call_response.id if call_response.id else ""
    )
    assert result["gen_ai.response.finish_reasons"] == (
        call_response.finish_reasons if call_response.finish_reasons else ""
    )
    assert result["gen_ai.usage.completion_tokens"] == (
        call_response.output_tokens if call_response.output_tokens else ""
    )
    assert result["gen_ai.usage.prompt_tokens"] == (
        call_response.input_tokens if call_response.input_tokens else ""
    )


def test_set_call_response_event_attributes() -> None:
    """Tests the `_set_call_response_event_attributes` function."""
    result = MagicMock()
    result.user_message_param = {"role": "user", "content": "user_content"}
    result.message_param = {"role": "assistant", "content": "assistant_content"}
    span = MagicMock()
    add_event = MagicMock()
    span.add_event = add_event

    _utils._set_call_response_event_attributes(result, span)
    assert add_event.call_count == 2
    assert add_event.call_args_list[0][0][0] == "gen_ai.content.prompt"
    assert add_event.call_args_list[0][1]["attributes"]["gen_ai.prompt"] == json.dumps(
        result.user_message_param
    )
    assert add_event.call_args_list[1][0][0] == "gen_ai.content.completion"
    assert add_event.call_args_list[1][1]["attributes"][
        "gen_ai.completion"
    ] == json.dumps(result.message_param)


@patch(
    "mirascope.integrations.otel._utils._get_call_response_attributes",
    new_callable=MagicMock,
    return_value={},
)
@patch(
    "mirascope.integrations.otel._utils._set_call_response_event_attributes",
    new_callable=MagicMock,
    return_value={},
)
def test_handle_call_response(
    mock_set_call_response_event_attributes: MagicMock,
    mock_get_call_response_attributes: MagicMock,
) -> None:
    """Tests the `handle_call_response` function."""
    mock_fn = MagicMock()
    assert _utils.handle_call_response(MagicMock(), mock_fn, None) is None

    result = MagicMock()
    result.tools = [
        FormatBook(title="The Name of the Wind", author="Rothfuss, Patrick")
    ]
    span = MagicMock()
    set_attributes = MagicMock()
    span.set_attributes = set_attributes
    _utils.handle_call_response(result, mock_fn, span)
    assert set_attributes.call_count == 1
    mock_get_call_response_attributes.assert_called_once_with(result)
    assert mock_get_call_response_attributes.return_value["async"] is False
    mock_set_call_response_event_attributes.assert_called_once_with(result, span)


@patch(
    "mirascope.integrations.otel._utils._get_call_response_attributes",
    new_callable=MagicMock,
    return_value={},
)
@patch(
    "mirascope.integrations.otel._utils._set_call_response_event_attributes",
    new_callable=MagicMock,
    return_value={},
)
@pytest.mark.asyncio
async def test_handle_call_response_async(
    mock_set_call_response_event_attributes: MagicMock,
    mock_get_call_response_attributes: MagicMock,
) -> None:
    """Tests the `handle_call_response_async` function."""
    mock_fn = MagicMock()
    assert await _utils.handle_call_response_async(MagicMock(), mock_fn, None) is None

    result = MagicMock()
    result.tools = [
        FormatBook(title="The Name of the Wind", author="Rothfuss, Patrick")
    ]
    span = MagicMock()
    set_attributes = MagicMock()
    span.set_attributes = set_attributes
    await _utils.handle_call_response_async(result, mock_fn, span)
    assert set_attributes.call_count == 1
    mock_get_call_response_attributes.assert_called_once_with(result)
    assert mock_get_call_response_attributes.return_value["async"] is True
    mock_set_call_response_event_attributes.assert_called_once_with(result, span)


@patch(
    "mirascope.integrations.otel._utils._get_call_response_attributes",
    new_callable=MagicMock,
    return_value={},
)
@patch(
    "mirascope.integrations.otel._utils._set_call_response_event_attributes",
    new_callable=MagicMock,
    return_value={},
)
def test_handle_stream(
    mock_set_call_response_event_attributes: MagicMock,
    mock_get_call_response_attributes: MagicMock,
) -> None:
    """Tests the `handle_stream` function."""
    mock_fn = MagicMock()
    assert _utils.handle_stream(MagicMock(), mock_fn, None) is None

    span = MagicMock()
    set_attributes = MagicMock()
    result = MagicMock(spec=BaseStream)
    mock_construct_call_response = MagicMock()
    result.construct_call_response = mock_construct_call_response
    span.set_attributes = set_attributes
    _utils.handle_stream(result, mock_fn, span)
    assert set_attributes.call_count == 1
    mock_get_call_response_attributes.assert_called_once_with(
        mock_construct_call_response()
    )
    assert mock_get_call_response_attributes.return_value["async"] is False
    mock_set_call_response_event_attributes.assert_called_once_with(
        mock_construct_call_response(), span
    )


@patch(
    "mirascope.integrations.otel._utils._get_call_response_attributes",
    new_callable=MagicMock,
    return_value={},
)
@patch(
    "mirascope.integrations.otel._utils._set_call_response_event_attributes",
    new_callable=MagicMock,
    return_value={},
)
@pytest.mark.asyncio
async def test_handle_stream_async(
    mock_set_call_response_event_attributes: MagicMock,
    mock_get_call_response_attributes: MagicMock,
) -> None:
    """Tests the `handle_stream_async` function."""
    mock_fn = MagicMock()
    assert await _utils.handle_stream_async(MagicMock(), mock_fn, None) is None

    span = MagicMock()
    set_attributes = MagicMock()
    result = MagicMock(spec=BaseStream)
    mock_construct_call_response = MagicMock()
    result.construct_call_response = mock_construct_call_response
    span.set_attributes = set_attributes
    await _utils.handle_stream_async(result, mock_fn, span)
    assert set_attributes.call_count == 1
    mock_get_call_response_attributes.assert_called_once_with(
        mock_construct_call_response()
    )
    assert mock_get_call_response_attributes.return_value["async"] is True
    mock_set_call_response_event_attributes.assert_called_once_with(
        mock_construct_call_response(), span
    )


@patch(
    "mirascope.integrations.otel._utils._get_call_response_attributes",
    new_callable=MagicMock,
    return_value={},
)
def test_handle_response_model(
    mock_get_call_response_attributes: MagicMock,
) -> None:
    """Tests the `handle_response_model` function with `BaseModel` result."""
    mock_fn = MagicMock()
    assert _utils.handle_response_model(MagicMock(), mock_fn, None) is None

    result = MagicMock(spec=BaseModel)
    response = MagicMock()
    result._response = response
    response.user_message_param = {"role": "user", "content": "user_content"}
    span = MagicMock()
    add_event = MagicMock()
    span.add_event = add_event
    set_attributes = MagicMock()
    span.set_attributes = set_attributes
    _utils.handle_response_model(result, mock_fn, span)
    assert set_attributes.call_count == 1
    mock_get_call_response_attributes.assert_called_once_with(response)
    assert mock_get_call_response_attributes.return_value["async"] is False

    assert add_event.call_count == 2
    assert add_event.call_args_list[0][0][0] == "gen_ai.content.prompt"
    assert add_event.call_args_list[0][1]["attributes"]["gen_ai.prompt"] == json.dumps(
        response.user_message_param
    )
    assert add_event.call_args_list[1][0][0] == "gen_ai.content.completion"
    assert (
        add_event.call_args_list[1][1]["attributes"]["gen_ai.completion"]
        == result.model_dump_json()
    )


def test_handle_response_model_base_type() -> None:
    """Tests the `handle_response_model` function with `BaseType` result."""
    mock_fn = MagicMock()
    result = b"foo"
    span = MagicMock()
    add_event = MagicMock()
    span.add_event = add_event
    set_attributes = MagicMock()
    span.set_attributes = set_attributes
    _utils.handle_response_model(result, mock_fn, span)
    assert set_attributes.call_count == 1
    set_attributes.assert_called_once_with({"async": False})
    assert add_event.call_count == 1
    assert add_event.call_args_list[0][0][0] == "gen_ai.content.completion"
    assert add_event.call_args_list[0][1]["attributes"]["gen_ai.completion"] == str(
        result
    )


@patch(
    "mirascope.integrations.otel._utils._get_call_response_attributes",
    new_callable=MagicMock,
    return_value={},
)
def test_handle_structured_stream(
    mock_get_call_response_attributes: MagicMock,
) -> None:
    """Tests the `handle_structured_stream` function."""
    mock_fn = MagicMock()
    assert _utils.handle_structured_stream(MagicMock(), mock_fn, None) is None

    class Foo(BaseModel):
        bar: str

    result = MagicMock(spec=BaseStructuredStream)
    response = MagicMock()
    result.stream = response
    result.constructed_response_model = Foo(bar="baz")
    response.user_message_param = {"role": "user", "content": "user_content"}
    mock_construct_call_response = MagicMock()
    response.construct_call_response = mock_construct_call_response
    span = MagicMock()
    add_event = MagicMock()
    span.add_event = add_event
    set_attributes = MagicMock()
    span.set_attributes = set_attributes
    _utils.handle_structured_stream(result, mock_fn, span)
    assert set_attributes.call_count == 1
    mock_get_call_response_attributes.assert_called_once_with(
        mock_construct_call_response()
    )
    assert mock_get_call_response_attributes.return_value["async"] is False

    assert add_event.call_count == 2
    assert add_event.call_args_list[0][0][0] == "gen_ai.content.prompt"
    assert add_event.call_args_list[0][1]["attributes"]["gen_ai.prompt"] == json.dumps(
        response.user_message_param
    )
    assert add_event.call_args_list[1][0][0] == "gen_ai.content.completion"
    assert (
        add_event.call_args_list[1][1]["attributes"]["gen_ai.completion"]
        == Foo(bar="baz").model_dump_json()
    )
    result.constructed_response_model = "test"
    _utils.handle_structured_stream(result, mock_fn, span)
    assert add_event.call_args_list[3][1]["attributes"]["gen_ai.completion"] == "test"


@patch(
    "mirascope.integrations.otel._utils._get_call_response_attributes",
    new_callable=MagicMock,
    return_value={},
)
@pytest.mark.asyncio
async def test_handle_response_model_async(
    mock_get_call_response_attributes: MagicMock,
) -> None:
    """Tests the `handle_response_model_async` function with `BaseModel` result."""
    mock_fn = MagicMock()
    assert await _utils.handle_response_model_async(MagicMock(), mock_fn, None) is None

    result = MagicMock(spec=BaseModel)
    response = MagicMock()
    result._response = response
    response.user_message_param = {"role": "user", "content": "user_content"}
    span = MagicMock()
    add_event = MagicMock()
    span.add_event = add_event
    set_attributes = MagicMock()
    span.set_attributes = set_attributes
    await _utils.handle_response_model_async(result, mock_fn, span)
    assert set_attributes.call_count == 1
    mock_get_call_response_attributes.assert_called_once_with(response)
    assert mock_get_call_response_attributes.return_value["async"] is True

    assert add_event.call_count == 2
    assert add_event.call_args_list[0][0][0] == "gen_ai.content.prompt"
    assert add_event.call_args_list[0][1]["attributes"]["gen_ai.prompt"] == json.dumps(
        response.user_message_param
    )
    assert add_event.call_args_list[1][0][0] == "gen_ai.content.completion"
    assert (
        add_event.call_args_list[1][1]["attributes"]["gen_ai.completion"]
        == result.model_dump_json()
    )


@pytest.mark.asyncio
async def test_handle_response_model_async_base_type() -> None:
    """Tests the `handle_response_model_async` function with `BaseType` result."""
    mock_fn = MagicMock()
    result = b"foo"
    span = MagicMock()
    add_event = MagicMock()
    span.add_event = add_event
    set_attributes = MagicMock()
    span.set_attributes = set_attributes
    await _utils.handle_response_model_async(result, mock_fn, span)
    assert set_attributes.call_count == 1
    set_attributes.assert_called_once_with({"async": True})
    assert add_event.call_count == 1
    assert add_event.call_args_list[0][0][0] == "gen_ai.content.completion"
    assert add_event.call_args_list[0][1]["attributes"]["gen_ai.completion"] == str(
        result
    )


@patch(
    "mirascope.integrations.otel._utils._get_call_response_attributes",
    new_callable=MagicMock,
    return_value={},
)
@pytest.mark.asyncio
async def test_handle_structured_stream_async(
    mock_get_call_response_attributes: MagicMock,
) -> None:
    """Tests the `handle_structured_stream_async` function."""
    mock_fn = MagicMock()
    assert (
        await _utils.handle_structured_stream_async(MagicMock(), mock_fn, None) is None
    )

    class Foo(BaseModel):
        bar: str

    result = MagicMock(spec=BaseStructuredStream)
    response = MagicMock()
    result.stream = response
    result.constructed_response_model = Foo(bar="baz")
    response.user_message_param = {"role": "user", "content": "user_content"}
    mock_construct_call_response = MagicMock()
    response.construct_call_response = mock_construct_call_response
    span = MagicMock()
    add_event = MagicMock()
    span.add_event = add_event
    set_attributes = MagicMock()
    span.set_attributes = set_attributes
    await _utils.handle_structured_stream_async(result, mock_fn, span)
    assert set_attributes.call_count == 1
    mock_get_call_response_attributes.assert_called_once_with(
        mock_construct_call_response()
    )
    assert mock_get_call_response_attributes.return_value["async"] is True

    assert add_event.call_count == 2
    assert add_event.call_args_list[0][0][0] == "gen_ai.content.prompt"
    assert add_event.call_args_list[0][1]["attributes"]["gen_ai.prompt"] == json.dumps(
        response.user_message_param
    )
    assert add_event.call_args_list[1][0][0] == "gen_ai.content.completion"
    assert (
        add_event.call_args_list[1][1]["attributes"]["gen_ai.completion"]
        == Foo(bar="baz").model_dump_json()
    )
    result.constructed_response_model = "test"
    await _utils.handle_structured_stream_async(result, mock_fn, span)
    assert add_event.call_args_list[3][1]["attributes"]["gen_ai.completion"] == "test"
