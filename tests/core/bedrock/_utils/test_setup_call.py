from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from types_aiobotocore_bedrock_runtime import (
    BedrockRuntimeClient as AsyncBedrockRuntimeClient,
)

from mirascope.core.bedrock._utils._setup_call import (
    _extract_async_stream_fn,
    _extract_sync_stream_fn,
    _get_async_client,
    setup_call,
)
from mirascope.core.bedrock.tool import BedrockTool


@pytest.fixture()
def mock_base_setup_call() -> MagicMock:
    mock_setup_call = MagicMock()
    mock_setup_call.return_value = [MagicMock() for _ in range(3)] + [{}]
    return mock_setup_call


@pytest.mark.asyncio
async def test_get_async_client():
    mock_session = MagicMock()

    mock_client = MagicMock(spec=AsyncBedrockRuntimeClient)
    mock_session.create_client.return_value.__aenter__.return_value = mock_client

    client = await _get_async_client(mock_session)

    assert isinstance(client, MagicMock)
    assert client == mock_client
    mock_session.create_client.assert_called_once_with("bedrock-runtime")


def test_extract_sync_stream_fn():
    mock_fn = MagicMock()
    mock_fn.return_value = {
        "ResponseMetadata": {"RequestId": "123"},
        "stream": [
            {
                "contentBlockDelta": {"delta": [{"text": "Hello"}]},
            },
            {
                "contentBlockDelta": {"delta": [{"text": "World"}]},
            },
        ],
    }

    extracted_fn = _extract_sync_stream_fn(mock_fn, "test-model")
    result = list(extracted_fn())

    assert len(result) == 2
    assert result[0]["contentBlockDelta"]["delta"][0]["text"] == "Hello"  # pyright: ignore [reportTypedDictNotRequiredAccess, reportGeneralTypeIssues]
    assert result[1]["contentBlockDelta"]["delta"][0]["text"] == "World"  # pyright: ignore [reportTypedDictNotRequiredAccess, reportGeneralTypeIssues]
    assert all(chunk["responseMetadata"] == {"RequestId": "123"} for chunk in result)
    assert all(chunk["model"] == "test-model" for chunk in result)


@pytest.mark.asyncio
async def test_extract_async_stream_fn():
    async def async_generator():
        yield {"chunk1": "async_data1"}
        yield {"chunk2": "async_data2"}

    mock_fn = AsyncMock()
    mock_fn.return_value = {
        "ResponseMetadata": {"RequestId": "456"},
        "stream": async_generator(),
    }

    extracted_fn = _extract_async_stream_fn(mock_fn, "test-async-model")
    result = [chunk async for chunk in extracted_fn()]

    assert len(result) == 2
    assert result[0]["chunk1"] == "async_data1"  # pyright: ignore [reportGeneralTypeIssues]
    assert result[1]["chunk2"] == "async_data2"  # pyright: ignore [reportGeneralTypeIssues]
    assert all(chunk["responseMetadata"] == {"RequestId": "456"} for chunk in result)
    assert all(chunk["model"] == "test-async-model" for chunk in result)


@patch(
    "mirascope.core.bedrock._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.bedrock._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call(
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    mock_utils.setup_call = mock_base_setup_call
    mock_base_setup_call.return_value[3] = {}
    fn = MagicMock()
    create, prompt_template, messages, tool_types, call_kwargs = setup_call(
        model="anthropic.claude-v2",
        client=None,
        fn=fn,
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params={},
        extract=False,
    )
    assert prompt_template == mock_base_setup_call.return_value[0]
    assert tool_types == mock_base_setup_call.return_value[2]
    assert "modelId" in call_kwargs and call_kwargs["modelId"] == "anthropic.claude-v2"
    assert "messages" in call_kwargs and call_kwargs["messages"] == messages
    mock_base_setup_call.assert_called_once_with(fn, {}, None, None, BedrockTool, {})
    mock_convert_message_params.assert_called_once_with(
        mock_base_setup_call.return_value[1]
    )
    assert messages == mock_convert_message_params.return_value


@patch("mirascope.core.bedrock._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_system_message(
    mock_utils: MagicMock, mock_base_setup_call: MagicMock
) -> None:
    mock_base_setup_call.return_value[1] = [
        {"role": "system", "content": [{"text": "system test"}]},
        {"role": "user", "content": [{"text": "user test"}]},
    ]
    mock_utils.setup_call = mock_base_setup_call
    mock_base_setup_call.return_value[3] = {}
    _, _, messages, _, _ = setup_call(
        model="anthropic.claude-v2",
        client=None,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params={},
        extract=False,
    )
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == [{"text": "user test"}]


@patch(
    "mirascope.core.bedrock._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.bedrock._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_json_mode(
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    mock_utils.setup_call = mock_base_setup_call
    mock_utils.json_mode_content = MagicMock(return_value="json_content")
    mock_base_setup_call.return_value[1] = [
        {"role": "user", "content": [{"text": "test"}]}
    ]
    mock_base_setup_call.return_value[3] = {"tools": MagicMock()}
    mock_convert_message_params.side_effect = lambda x: x
    _, _, messages, _, call_kwargs = setup_call(
        model="anthropic.claude-v2",
        client=None,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=True,
        call_params={},
        extract=False,
    )
    assert messages[-1]["content"] == [{"text": "testjson_content"}]
    assert "tools" not in call_kwargs


@patch(
    "mirascope.core.bedrock._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.bedrock._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_json_mode_no_text(
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    mock_utils.setup_call = mock_base_setup_call
    mock_utils.json_mode_content = MagicMock(return_value="json_content")
    mock_base_setup_call.return_value[1] = [
        {"role": "user", "content": [{"image": "test_image"}]}
    ]
    mock_base_setup_call.return_value[3] = {"tools": MagicMock()}
    mock_convert_message_params.side_effect = lambda x: x
    _, _, messages, _, call_kwargs = setup_call(
        model="anthropic.claude-v2",
        client=None,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=True,
        call_params={},
        extract=False,
    )
    assert messages[-1]["content"] == [
        {"image": "test_image"},
        {"text": "json_content"},
    ]
    assert "tools" not in call_kwargs


@patch(
    "mirascope.core.bedrock._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.bedrock._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_extract(
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    tool_mock = MagicMock(spec=BedrockTool, __name__="tool")
    tool_mock._name.return_value = "mock_tool"
    mock_base_setup_call.return_value[2] = [tool_mock]
    mock_base_setup_call.return_value[3] = {"toolConfig": {}}
    mock_utils.setup_call = mock_base_setup_call
    _, _, _, tool_types, call_kwargs = setup_call(
        model="anthropic.claude-v2",
        client=None,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params={},
        extract=True,
    )
    assert isinstance(tool_types, list)
    assert "toolConfig" in call_kwargs and call_kwargs["toolConfig"] == {
        "toolChoice": {"name": "mock_tool", "type": "tool"}
    }


@patch(
    "mirascope.core.bedrock._utils._setup_call.convert_message_params",
    new_callable=MagicMock,
)
@patch("mirascope.core.bedrock._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_with_tools(
    mock_utils: MagicMock,
    mock_convert_message_params: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    mock_utils.setup_call = mock_base_setup_call
    mock_base_setup_call.return_value[3] = {"tools": [{"name": "test_tool"}]}
    fn = MagicMock()
    _, _, _, _, call_kwargs = setup_call(
        model="anthropic.claude-v2",
        client=None,
        fn=fn,
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params={},
        extract=False,
    )
    assert "toolConfig" in call_kwargs
    assert call_kwargs["toolConfig"] == {"tools": [{"name": "test_tool"}]}


@patch("mirascope.core.bedrock._utils._setup_call._get_async_client")
@patch("mirascope.core.bedrock._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_client_creation(
    mock_utils: MagicMock,
    mock_get_async_client: AsyncMock,
    mock_base_setup_call: MagicMock,
) -> None:
    mock_utils.setup_call = mock_base_setup_call
    mock_base_setup_call.return_value[1] = [
        {"role": "user", "content": [{"text": "user test"}]},
    ]
    mock_base_setup_call.return_value[3] = {}

    # Test sync client creation
    setup_call(
        model="anthropic.claude-v2",
        client=None,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params={},
        extract=False,
    )

    # Test async client creation
    async def async_fn(): ...

    setup_call(
        model="anthropic.claude-v2",
        client=None,
        fn=async_fn,
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params={},
        extract=False,
    )
    mock_get_async_client.assert_called_once()

    # Test when client is provided
    mock_client = MagicMock()
    setup_call(
        model="anthropic.claude-v2",
        client=mock_client,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params={},
        extract=False,
    )
    assert mock_get_async_client.call_count == 1
