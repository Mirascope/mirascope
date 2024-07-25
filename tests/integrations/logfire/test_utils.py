from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel, Field

from mirascope.core.base._stream import BaseStream
from mirascope.core.base._structured_stream import BaseStructuredStream
from mirascope.core.base.call_response import BaseCallResponse
from mirascope.core.base.metadata import Metadata
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

    @property
    def tools(self) -> list[BaseTool]:
        return [FormatBook(title="The Name of the Wind", author="Rothfuss, Patrick")]


patch.multiple(MyCallResponse, __abstractmethods__=set()).start()
patch.multiple(BaseStream, __abstractmethods__=set()).start()


class MyStream(BaseStream):
    _provider = "test"

    @property
    def cost(self):
        return 10


@patch("logfire.with_settings", new_callable=MagicMock)
def test_logfire_custom_context_manager(mock_logfire: MagicMock) -> None:
    """Tests the `custom_context_manager` context manager."""
    mock_fn = MagicMock()
    mock_fn.__name__ = "mock_fn"
    mock_fn.__annotations__ = {"metadata": Metadata(tags={"tag1", "tag2"})}

    with _utils.custom_context_manager(mock_fn):
        mock_logfire.assert_called_once()
        call_args = mock_logfire.call_args[1]
        assert call_args["custom_scope_suffix"] == "mirascope"
        assert isinstance(call_args["tags"], list)
        assert set(call_args["tags"]) == {"tag1", "tag2"}


def test_get_call_response_span_data():
    call_response = MagicMock()
    result = _utils.get_call_response_span_data(call_response)
    assert result["async"] is False
    assert result["call_params"] == call_response.call_params
    assert result["call_kwargs"] == call_response.call_kwargs
    assert result["model"] == call_response.model
    assert result["provider"] == call_response._provider
    assert result["prompt_template"] == call_response.prompt_template
    assert result["template_variables"] == call_response.fn_args
    assert result["messages"] == call_response.messages
    assert result["response_data"] == call_response.response


def test_get_stream_span_data():
    mock_chunk = MagicMock()
    mock_chunk.content = "content"
    mock_chunk.input_tokens = 1
    mock_chunk.output_tokens = 2
    mock_chunk.model = "updated_model"
    stream_chunks = [(mock_chunk, None)]
    content = "mock_message_param"
    my_stream = MyStream(
        stream=(t for t in stream_chunks),
        metadata={"tags": {"bar"}},
        tool_types=[],
        call_response_type=MagicMock,
        model="model",
        prompt_template="prompt_template",
        fn_args={"hello": "world"},
        dynamic_config=None,
        messages=[{"role": "user", "content": "mock_message"}],
        call_params={"a": "b"},
        call_kwargs={"c": "d"},
    )  # type: ignore
    my_stream.message_param = {"role": "assistant", "content": content}
    result = _utils.get_stream_span_data(my_stream)
    assert result["messages"] == [my_stream.user_message_param]
    assert result["call_params"] == my_stream.call_params
    assert result["call_kwargs"] == my_stream.call_kwargs
    assert result["model"] == my_stream.model
    assert result["provider"] == my_stream._provider
    assert result["prompt_template"] == my_stream.prompt_template
    assert result["template_variables"] == my_stream.fn_args
    assert result["output"]["cost"] == my_stream.cost
    assert result["output"]["content"] == content


def test_get_tool_calls():
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
    result = _utils.get_tool_calls(call_response)
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
    assert _utils.get_tool_calls(result) is None


def test_get_output():
    result = MagicMock()
    result.cost = 10
    result.input_tokens = 1
    result.output_tokens = 2
    result_content = "content"
    result.content = result_content
    assert _utils.get_output(result) == {
        "cost": 10,
        "input_tokens": 1,
        "output_tokens": 2,
        "content": result_content,
    }


@patch("mirascope.integrations.logfire._utils.get_output", new_callable=MagicMock)
@patch(
    "mirascope.integrations.logfire._utils.get_call_response_span_data",
    new_callable=MagicMock,
    return_value={},
)
@patch("mirascope.integrations.logfire._utils.get_tool_calls", new_callable=MagicMock)
def test_handle_call_response(
    mock_get_tool_calls: MagicMock,
    mock_get_call_response_span_data: MagicMock,
    mock_get_output: MagicMock,
):
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
    mock_get_output.assert_called_once_with(result)
    mock_get_tool_calls.assert_called_once_with(result)
    mock_get_call_response_span_data.assert_called_once_with(result)
    assert mock_get_call_response_span_data.return_value["async"] is False
    assert (
        set_attributes.call_args[0][0] == mock_get_call_response_span_data.return_value
    )


@patch("mirascope.integrations.logfire._utils.get_output", new_callable=MagicMock)
@patch(
    "mirascope.integrations.logfire._utils.get_call_response_span_data",
    new_callable=MagicMock,
    return_value={},
)
@patch("mirascope.integrations.logfire._utils.get_tool_calls", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_handle_call_response_async(
    mock_get_tool_calls: MagicMock,
    mock_get_call_response_span_data: MagicMock,
    mock_get_output: MagicMock,
):
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
    mock_get_output.assert_called_once_with(result)
    mock_get_tool_calls.assert_called_once_with(result)
    mock_get_call_response_span_data.assert_called_once_with(result)
    assert mock_get_call_response_span_data.return_value["async"] is True
    assert (
        set_attributes.call_args[0][0] == mock_get_call_response_span_data.return_value
    )


@patch(
    "mirascope.integrations.logfire._utils.get_stream_span_data",
    new_callable=MagicMock,
    return_value={},
)
def test_handle_stream(mock_get_stream_span_data: MagicMock):
    mock_fn = MagicMock()
    assert _utils.handle_stream(MagicMock(), mock_fn, None) is None

    stream = MagicMock()
    span = MagicMock()
    span.set_attributes = MagicMock()
    _utils.handle_stream(stream, mock_fn, span)
    mock_get_stream_span_data.assert_called_once_with(stream)
    call_args = span.set_attributes.call_args[0][0]
    assert call_args["async"] is False
    assert call_args == mock_get_stream_span_data.return_value


@patch(
    "mirascope.integrations.logfire._utils.get_stream_span_data",
    new_callable=MagicMock,
    return_value={},
)
@pytest.mark.asyncio
async def test_handle_stream_async(mock_get_stream_span_data: MagicMock):
    mock_fn = MagicMock()
    assert await _utils.handle_stream_async(MagicMock(), mock_fn, None) is None

    stream = MagicMock()
    span = MagicMock()
    span.set_attributes = MagicMock()
    await _utils.handle_stream_async(stream, mock_fn, span)
    mock_get_stream_span_data.assert_called_once_with(stream)
    call_args = span.set_attributes.call_args[0][0]
    assert call_args["async"] is True
    assert call_args == mock_get_stream_span_data.return_value


@patch(
    "mirascope.integrations.logfire._utils.get_call_response_span_data",
    new_callable=MagicMock,
    return_value={},
)
@patch(
    "mirascope.integrations.logfire._utils.get_output",
    new_callable=MagicMock,
    return_value={},
)
def test_handle_base_model(
    mock_get_output: MagicMock,
    mock_get_call_response_span_data: MagicMock,
):
    mock_fn = MagicMock()
    assert _utils.handle_base_model(MagicMock(), mock_fn, None) is None

    base_model_result = MagicMock(spec=BaseModel)
    base_model_result._response = MagicMock(spec=BaseCallResponse)
    span = MagicMock()
    _utils.handle_base_model(base_model_result, mock_fn, span)
    mock_get_call_response_span_data.assert_called_once_with(
        base_model_result._response
    )
    mock_get_output.assert_called_once_with(base_model_result._response)
    assert mock_get_call_response_span_data.return_value["async"] is False
    assert mock_get_output.return_value["response_model"] == base_model_result


@patch(
    "mirascope.integrations.logfire._utils.get_stream_span_data",
    new_callable=MagicMock,
    return_value={},
)
def test_handle_structured_stream(
    mock_get_stream_span_data: MagicMock,
):
    mock_fn = MagicMock()
    assert _utils.handle_structured_stream(MagicMock(), mock_fn, None) is None

    span = MagicMock()
    base_structured_stream_result = MagicMock(spec=BaseStructuredStream)
    base_structured_stream_result.constructed_response_model = MagicMock(spec=BaseModel)
    base_structured_stream_result.stream = MagicMock(spec=BaseStream)
    _utils.handle_structured_stream(base_structured_stream_result, mock_fn, span)
    mock_get_stream_span_data.assert_called_once_with(
        base_structured_stream_result.stream
    )
    assert mock_get_stream_span_data.return_value["output"]["response_model"] == (
        base_structured_stream_result.constructed_response_model
    )
    assert mock_get_stream_span_data.return_value["async"] is False


@patch(
    "mirascope.integrations.logfire._utils.get_call_response_span_data",
    new_callable=MagicMock,
    return_value={},
)
@patch(
    "mirascope.integrations.logfire._utils.get_output",
    new_callable=MagicMock,
    return_value={},
)
@pytest.mark.asyncio
async def test_handle_base_model_async(
    mock_get_output: MagicMock,
    mock_get_call_response_span_data: MagicMock,
):
    mock_fn = MagicMock()
    assert await _utils.handle_base_model_async(MagicMock(), mock_fn, None) is None

    base_model_result = MagicMock(spec=BaseModel)
    base_model_result._response = MagicMock(spec=BaseCallResponse)
    span = MagicMock()
    await _utils.handle_base_model_async(base_model_result, mock_fn, span)
    mock_get_call_response_span_data.assert_called_once_with(
        base_model_result._response
    )
    mock_get_output.assert_called_once_with(base_model_result._response)
    assert mock_get_call_response_span_data.return_value["async"] is True
    assert mock_get_output.return_value["response_model"] == base_model_result


@patch(
    "mirascope.integrations.logfire._utils.get_stream_span_data",
    new_callable=MagicMock,
    return_value={},
)
@pytest.mark.asyncio
async def test_structured_stream_async(
    mock_get_stream_span_data: MagicMock,
):
    mock_fn = MagicMock()
    assert (
        await _utils.handle_structured_stream_async(MagicMock(), mock_fn, None) is None
    )

    span = MagicMock()

    base_structured_stream_result = MagicMock(spec=BaseStructuredStream)
    base_structured_stream_result.constructed_response_model = MagicMock(spec=BaseModel)
    base_structured_stream_result.stream = MagicMock(spec=BaseStream)
    await _utils.handle_structured_stream_async(
        base_structured_stream_result, mock_fn, span
    )
    mock_get_stream_span_data.assert_called_once_with(
        base_structured_stream_result.stream
    )
    assert mock_get_stream_span_data.return_value["output"]["response_model"] == (
        base_structured_stream_result.constructed_response_model
    )
    assert mock_get_stream_span_data.return_value["async"] is True
