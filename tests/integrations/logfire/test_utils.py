from contextlib import suppress
from functools import cached_property
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, Field

from mirascope.core.base.call_response import BaseCallResponse
from mirascope.core.base.metadata import Metadata
from mirascope.core.base.stream import BaseStream
from mirascope.core.base.structured_stream import BaseStructuredStream
from mirascope.core.base.tool import BaseTool
from mirascope.integrations.logfire import _utils


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
        return [FormatBook(title="The Name of the Wind", author="Rothfuss, Patrick")]


patch.multiple(MyCallResponse, __abstractmethods__=set()).start()
patch.multiple(BaseStream, __abstractmethods__=set()).start()


@patch("logfire.with_settings", new_callable=MagicMock)
def test_logfire_custom_context_manager(mock_logfire: MagicMock) -> None:
    """Tests the `custom_context_manager` context manager."""
    mock_fn = MagicMock()
    mock_fn.__name__ = "mock_fn"
    mock_fn._metadata = Metadata(tags={"tag1", "tag2"})

    with _utils.custom_context_manager(mock_fn):
        mock_logfire.assert_called_once()
        call_args = mock_logfire.call_args[1]
        assert call_args["custom_scope_suffix"] == "mirascope"
        assert isinstance(call_args["tags"], list)
        assert set(call_args["tags"]) == {"tag1", "tag2"}


def test_get_call_response_span_data() -> None:
    call_response = MagicMock()
    result = _utils._get_call_response_span_data(call_response)
    assert result["async"] is False
    assert result["call_params"] == call_response.call_params
    assert result["call_kwargs"] == call_response.call_kwargs
    assert result["model"] == call_response.model
    assert result["provider"] == call_response._provider
    assert result["prompt_template"] == call_response.prompt_template
    assert result["template_variables"] == call_response.fn_args
    assert result["messages"] == call_response.messages
    assert result["response_data"] == call_response.response
    assert result["output"] == {
        "cost": call_response.cost,
        "input_tokens": call_response.input_tokens,
        "output_tokens": call_response.output_tokens,
        "content": call_response.content,
    }


def test_get_tool_calls() -> None:
    call_response = MyCallResponse(
        metadata={"tags": {"version:0001"}},
        response="test response",
        tool_types=[],
        prompt_template="test prompt",
        fn_args={},
        dynamic_config={},
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param={},
        start_time=100,
        end_time=200,
    )  # type: ignore
    result = _utils._get_tool_calls(call_response)
    assert result == [
        {
            "function": {
                "arguments": {
                    "title": "The Name of the Wind",
                    "author": "Rothfuss, Patrick",
                },
                "name": "FormatBook",
            }
        }
    ]

    result = MagicMock()
    result.tools = None
    assert _utils._get_tool_calls(result) is None


@patch(
    "mirascope.integrations.logfire._utils._get_call_response_span_data",
    new_callable=MagicMock,
    return_value={},
)
@patch("mirascope.integrations.logfire._utils._get_tool_calls", new_callable=MagicMock)
def test_handle_call_response(
    mock_get_tool_calls: MagicMock,
    mock_get_call_response_span_data: MagicMock,
) -> None:
    mock_fn = MagicMock()
    assert _utils.handle_call_response(MagicMock(), mock_fn, None) is None

    result = MagicMock()
    result.tools = [
        FormatBook(title="The Name of the Wind", author="Rothfuss, Patrick")
    ]
    span = MagicMock()
    set_attributes = MagicMock()
    span.set_attributes = set_attributes
    mock_get_call_response_span_data.return_value = {"output": {}}
    _utils.handle_call_response(result, mock_fn, span)
    assert set_attributes.call_count == 1
    mock_get_tool_calls.assert_called_once_with(result)
    mock_get_call_response_span_data.assert_called_once_with(result)
    assert mock_get_call_response_span_data.return_value["async"] is False
    assert (
        set_attributes.call_args[0][0] == mock_get_call_response_span_data.return_value
    )


@patch(
    "mirascope.integrations.logfire._utils._get_call_response_span_data",
    new_callable=MagicMock,
    return_value={},
)
@patch("mirascope.integrations.logfire._utils._get_tool_calls", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_handle_call_response_async(
    mock_get_tool_calls: MagicMock,
    mock_get_call_response_span_data: MagicMock,
) -> None:
    mock_fn = MagicMock()
    assert await _utils.handle_call_response_async(MagicMock(), mock_fn, None) is None

    result = MagicMock()
    result.tools = [
        FormatBook(title="The Name of the Wind", author="Rothfuss, Patrick")
    ]
    span = MagicMock()
    set_attributes = MagicMock()
    span.set_attributes = set_attributes
    mock_get_call_response_span_data.return_value = {"output": {}}
    await _utils.handle_call_response_async(result, mock_fn, span)
    assert set_attributes.call_count == 1
    mock_get_tool_calls.assert_called_once_with(result)
    mock_get_call_response_span_data.assert_called_once_with(result)
    assert mock_get_call_response_span_data.return_value["async"] is True
    assert (
        set_attributes.call_args[0][0] == mock_get_call_response_span_data.return_value
    )


@patch(
    "mirascope.integrations.logfire._utils.handle_call_response", new_callable=MagicMock
)
def test_handle_stream(mock_handle_call_response: MagicMock) -> None:
    mock_fn = MagicMock()
    mock_stream = MagicMock(spec=BaseStream)
    construct_call_response = MagicMock()
    mock_span = MagicMock()
    mock_stream.construct_call_response.return_value = construct_call_response
    _utils.handle_stream(mock_stream, mock_fn, mock_span)
    mock_handle_call_response.assert_called_once_with(
        construct_call_response, mock_fn, mock_span
    )


@patch(
    "mirascope.integrations.logfire._utils.handle_call_response_async",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_handle_stream_async(mock_handle_call_response_async: MagicMock) -> None:
    mock_fn = MagicMock()
    mock_stream = MagicMock(spec=BaseStream)
    construct_call_response = MagicMock()
    mock_span = MagicMock()
    mock_stream.construct_call_response.return_value = construct_call_response
    await _utils.handle_stream_async(mock_stream, mock_fn, mock_span)
    mock_handle_call_response_async.assert_called_once_with(
        construct_call_response, mock_fn, mock_span
    )


@patch(
    "mirascope.integrations.logfire._utils._get_call_response_span_data",
    new_callable=MagicMock,
    return_value={},
)
@patch(
    "mirascope.integrations.logfire._utils._set_response_model_output",
    new_callable=MagicMock,
    return_value={},
)
def test_handle_response_model(
    mock_set_response_model_output: MagicMock,
    mock_get_call_response_span_data: MagicMock,
) -> None:
    mock_fn = MagicMock()
    assert _utils.handle_response_model(MagicMock(), mock_fn, None) is None

    base_model_result = MagicMock(spec=BaseModel)
    base_model_result._response = MagicMock(spec=BaseCallResponse)
    span = MagicMock()
    mock_output = MagicMock()
    mock_set_attributes = MagicMock()
    span.set_attributes = mock_set_attributes
    mock_get_call_response_span_data.return_value = {"output": mock_output}
    _utils.handle_response_model(base_model_result, mock_fn, span)
    mock_get_call_response_span_data.assert_called_once_with(
        base_model_result._response
    )
    mock_set_response_model_output.assert_called_once_with(
        base_model_result, mock_get_call_response_span_data.return_value["output"]
    )
    mock_set_attributes.assert_called_once_with({"output": mock_output, "async": False})


@patch(
    "mirascope.integrations.logfire._utils._get_structured_stream_span_data",
    new_callable=MagicMock,
    return_value={},
)
def test_handle_structured_stream(
    mock_get_structured_stream_span_data: MagicMock,
) -> None:
    mock_fn = MagicMock()
    assert _utils.handle_structured_stream(MagicMock(), mock_fn, None) is None

    span = MagicMock()

    base_structured_stream_result = MagicMock(spec=BaseStructuredStream)
    base_structured_stream_result.constructed_response_model = MagicMock(spec=BaseModel)
    base_structured_stream_result.stream = MagicMock(spec=BaseStream)
    base_call_response = MagicMock(spec=BaseCallResponse)
    base_structured_stream_result.stream.construct_call_response.return_value = (
        base_call_response
    )
    _utils.handle_structured_stream(base_structured_stream_result, mock_fn, span)
    mock_get_structured_stream_span_data.assert_called_once_with(
        base_structured_stream_result
    )
    assert mock_get_structured_stream_span_data.return_value["async"] is False


@patch(
    "mirascope.integrations.logfire._utils._get_error_span_data",
    new_callable=MagicMock,
    return_value={},
)
def test_handle_error(mock_get_error_span_data: MagicMock) -> None:
    mock_get_error_span_data.return_value = {"error": "error"}
    _utils.handle_error(Exception("error"), MagicMock(), None)
    assert mock_get_error_span_data.call_count == 0
    span = MagicMock()
    with suppress(Exception):
        _utils.handle_error(Exception("error"), MagicMock(), span)
    assert span.set_attributes.call_count == 1
    assert span.set_attributes.call_args[0][0] == {"error": "error", "async": False}


@patch(
    "mirascope.integrations.logfire._utils._get_call_response_span_data",
    new_callable=MagicMock,
    return_value={},
)
@patch(
    "mirascope.integrations.logfire._utils._set_response_model_output",
    new_callable=MagicMock,
    return_value={},
)
@pytest.mark.asyncio
async def test_handle_response_model_async(
    mock_set_response_model_output: MagicMock,
    mock_get_call_response_span_data: MagicMock,
) -> None:
    mock_fn = MagicMock()
    assert await _utils.handle_response_model_async(MagicMock(), mock_fn, None) is None

    base_model_result = MagicMock(spec=BaseModel)
    base_model_result._response = MagicMock(spec=BaseCallResponse)
    span = MagicMock()
    mock_set_attributes = MagicMock()
    span.set_attributes = mock_set_attributes
    mock_output = MagicMock()
    mock_get_call_response_span_data.return_value = {"output": mock_output}
    await _utils.handle_response_model_async(base_model_result, mock_fn, span)
    mock_get_call_response_span_data.assert_called_once_with(
        base_model_result._response
    )
    mock_set_response_model_output.assert_called_once_with(
        base_model_result, mock_get_call_response_span_data.return_value["output"]
    )
    mock_set_attributes.assert_called_once_with({"output": mock_output, "async": True})


@patch(
    "mirascope.integrations.logfire._utils._get_structured_stream_span_data",
    new_callable=MagicMock,
    return_value={},
)
@pytest.mark.asyncio
async def test_handle_structured_stream_async(
    mock_get_structured_stream_span_data: MagicMock,
) -> None:
    mock_fn = MagicMock()
    assert (
        await _utils.handle_structured_stream_async(MagicMock(), mock_fn, None) is None
    )

    span = MagicMock()
    base_structured_stream_result = MagicMock(spec=BaseStructuredStream)
    base_structured_stream_result.constructed_response_model = MagicMock(spec=BaseModel)
    base_structured_stream_result.stream = MagicMock(spec=BaseStream)
    base_call_response = MagicMock(spec=BaseCallResponse)
    base_structured_stream_result.stream.construct_call_response.return_value = (
        base_call_response
    )
    await _utils.handle_structured_stream_async(
        base_structured_stream_result, mock_fn, span
    )
    mock_get_structured_stream_span_data.assert_called_once_with(
        base_structured_stream_result
    )
    assert mock_get_structured_stream_span_data.return_value["async"] is True


@patch(
    "mirascope.integrations.logfire._utils._get_error_span_data",
    new_callable=MagicMock,
    return_value={},
)
@pytest.mark.asyncio
async def test_handle_error_async(mock_get_error_span_data: MagicMock) -> None:
    mock_get_error_span_data.return_value = {"error": "error"}
    await _utils.handle_error_async(Exception("error"), MagicMock(), None)
    assert mock_get_error_span_data.call_count == 0
    span = MagicMock()
    with suppress(Exception):
        await _utils.handle_error_async(Exception("error"), MagicMock(), span)
    assert span.set_attributes.call_count == 1
    assert span.set_attributes.call_args[0][0] == {"error": "error", "async": True}


def test_set_response_model_output() -> None:
    class MyBaseModel(BaseModel):
        foo: str

    my_base_model_output = {}
    _utils._set_response_model_output(MyBaseModel(foo="bar"), my_base_model_output)
    assert my_base_model_output == {
        "response_model": {"name": "MyBaseModel", "arguments": {"foo": "bar"}}
    }
    my_base_type_output = {}
    _utils._set_response_model_output("foo", my_base_type_output)
    assert my_base_type_output == {"content": "foo"}


@patch(
    "mirascope.integrations.logfire._utils._get_call_response_span_data",
    new_callable=MagicMock,
    return_value={},
)
def test_get_structured_stream_span_data_base_model(
    mock_get_call_response_span_data: MagicMock,
) -> None:
    class MyBaseModel(BaseModel):
        foo: str

    mock_result = MagicMock(spec=BaseStructuredStream)
    mock_result.stream = MagicMock()
    mock_result.constructed_response_model = MyBaseModel(foo="bar")
    span_data = _utils._get_structured_stream_span_data(mock_result)
    assert span_data == {
        "output": {
            "response_model": {"name": "MyBaseModel", "arguments": {"foo": "bar"}}
        }
    }


@patch(
    "mirascope.integrations.logfire._utils._get_call_response_span_data",
    new_callable=MagicMock,
    return_value={},
)
def test_get_structured_stream_span_data_base_type(
    mock_get_call_response_span_data: MagicMock,
) -> None:
    class MyBaseModel(BaseModel):
        foo: str

    mock_result = MagicMock(spec=BaseStructuredStream)
    mock_result.stream = MagicMock()
    mock_result.constructed_response_model = "foo"
    span_data = _utils._get_structured_stream_span_data(mock_result)
    assert span_data == {"output": {"content": "foo"}}


@patch(
    "mirascope.integrations.logfire._utils._get_tool_calls",
    new_callable=MagicMock,
    return_value={},
)
@patch(
    "mirascope.integrations.logfire._utils._get_call_response_span_data",
    new_callable=MagicMock,
    return_value={},
)
def test_get_error_span_data(
    mock_get_call_response_span_data: MagicMock, mock_get_tool_calls: MagicMock
) -> None:
    mock_get_call_response_span_data.return_value = {"output": {"mock": "mock"}}
    mock_get_tool_calls.return_value = [{"function": "mock"}]
    error = Exception("error")
    error._response = MagicMock()  # pyright: ignore [reportAttributeAccessIssue]
    span_data = _utils._get_error_span_data(error, MagicMock())
    assert span_data == {
        "output": {"mock": "mock", "tool_calls": [{"function": "mock"}]},
        "error": "Exception",
        "error_message": "error",
    }
