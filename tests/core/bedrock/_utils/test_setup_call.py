from unittest.mock import AsyncMock, MagicMock, patch

import aiobotocore.client
import pytest
from aiobotocore.session import AioSession
from pydantic import BaseModel

from mirascope.core.bedrock._utils._convert_common_call_params import (
    convert_common_call_params,
)
from mirascope.core.bedrock._utils._setup_call import (
    _AsyncBedrockRuntimeWrappedClient,
    _extract_async_stream_fn,
    _extract_sync_stream_fn,
    setup_call,
)
from mirascope.core.bedrock.tool import BedrockTool


@pytest.fixture()
def mock_base_setup_call() -> MagicMock:
    mock_setup_call = MagicMock()
    mock_setup_call.return_value = [MagicMock() for _ in range(3)] + [{}]
    return mock_setup_call


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
        response_model=None,
        stream=False,
    )
    assert prompt_template == mock_base_setup_call.return_value[0]
    assert tool_types == mock_base_setup_call.return_value[2]
    assert "modelId" in call_kwargs and call_kwargs["modelId"] == "anthropic.claude-v2"
    assert "messages" in call_kwargs and call_kwargs["messages"] == messages
    mock_base_setup_call.assert_called_once_with(
        fn, {}, None, None, BedrockTool, {}, convert_common_call_params
    )
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
        response_model=None,
        stream=False,
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
        response_model=None,
        stream=False,
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
        response_model=None,
        stream=False,
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
        response_model=BaseModel,
        stream=False,
    )
    assert isinstance(tool_types, list)
    assert "toolConfig" in call_kwargs and call_kwargs["toolConfig"] == {
        "toolChoice": {
            "tool": {
                "name": "mock_tool",
            }
        }
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
        response_model=None,
        stream=False,
    )
    assert "toolConfig" in call_kwargs
    assert call_kwargs["toolConfig"] == {"tools": [{"name": "test_tool"}]}


@patch("mirascope.core.bedrock._utils._setup_call.get_session")
@patch("mirascope.core.bedrock._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_client_creation(
    mock_utils: MagicMock,
    mock_get_session: MagicMock,
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
        response_model=None,
        stream=False,
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
        response_model=None,
        stream=False,
    )

    mock_get_session.assert_called_once()

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
        response_model=None,
        stream=False,
    )


@patch("mirascope.core.bedrock._utils._setup_call.get_async_create_fn")
@patch("mirascope.core.bedrock._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_aiobotocore_client(
    mock_utils: MagicMock,
    mock_get_async_create_fn: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    """
    Test that when the provided client is an instance of aiobotocore.client.AioBaseClient,
    setup_call uses get_async_create_fn with client.converse and the _extract_async_stream_fn.
    """
    mock_utils.setup_call = mock_base_setup_call
    mock_base_setup_call.return_value = [
        "prompt",
        [{"role": "user", "content": [{"text": "test"}]}],
        None,
        {},
    ]

    mock_aiobotocore_client = MagicMock(spec=aiobotocore.client.AioBaseClient)
    mock_aiobotocore_client.converse = AsyncMock()
    mock_aiobotocore_client.converse_stream = AsyncMock()

    create, prompt_template, messages, tool_types, call_kwargs = setup_call(
        model="anthropic.claude-v2",
        client=mock_aiobotocore_client,
        fn=MagicMock(),  # can be any callable
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params={},
        response_model=None,
        stream=False,
    )

    mock_get_async_create_fn.assert_called_once()
    args, kwargs = mock_get_async_create_fn.call_args

    assert args[0] is mock_aiobotocore_client.converse
    assert callable(args[1])

    assert create == mock_get_async_create_fn.return_value

    assert prompt_template == "prompt"
    assert messages[0]["role"] == "user"
    assert call_kwargs["modelId"] == "anthropic.claude-v2"


@patch("mirascope.core.bedrock._utils._setup_call.get_async_create_fn")
@patch("mirascope.core.bedrock._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_async_bedrock_runtime_wrapped_client(
    mock_utils: MagicMock,
    mock_get_async_create_fn: MagicMock,
    mock_base_setup_call: MagicMock,
) -> None:
    """
    Test that when the provided client is an instance of _AsyncBedrockRuntimeWrappedClient,
    setup_call uses get_async_create_fn correctly with client.converse and client.converse_stream.
    """
    mock_utils.setup_call = mock_base_setup_call
    mock_base_setup_call.return_value = [
        "prompt",
        [{"role": "user", "content": [{"text": "test"}]}],
        None,
        {},
    ]

    wrapped_client = _AsyncBedrockRuntimeWrappedClient(
        MagicMock(), "anthropic.claude-v2"
    )

    create, prompt_template, messages, tool_types, call_kwargs = setup_call(  # pyright: ignore [reportCallIssue]
        model="anthropic.claude-v2",
        client=wrapped_client,  # pyright: ignore [reportArgumentType]
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params={},
        response_model=None,
        stream=False,
    )

    mock_get_async_create_fn.assert_called_once_with(
        wrapped_client.converse,
        wrapped_client.converse_stream,
    )
    assert create == mock_get_async_create_fn.return_value
    assert prompt_template == "prompt"
    assert messages[0]["role"] == "user"
    assert "modelId" in call_kwargs and call_kwargs["modelId"] == "anthropic.claude-v2"


@pytest.mark.asyncio
async def test_async_bedrock_runtime_wrapped_client_converse():
    """
    Test that _AsyncBedrockRuntimeWrappedClient.converse calls client.converse inside the context
    manager and returns the response.
    """
    mock_session = MagicMock(spec=AioSession)
    mock_client = AsyncMock()
    mock_client.converse = AsyncMock(return_value={"some": "result"})

    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = mock_client
    mock_context_manager.__aexit__.return_value = None

    mock_session.create_client.return_value = mock_context_manager

    wrapped_client = _AsyncBedrockRuntimeWrappedClient(mock_session, "test-model")
    result = await wrapped_client.converse(param1="value1")  # pyright: ignore [reportCallIssue]

    assert result == {"some": "result"}

    mock_client.converse.assert_called_once_with(param1="value1")

    mock_session.create_client.assert_called_once_with("bedrock-runtime")


@pytest.mark.asyncio
async def test_async_bedrock_runtime_wrapped_client_converse_stream():
    """
    Test that _AsyncBedrockRuntimeWrappedClient.converse_stream calls client.converse_stream
    and yields dicts with the correct keys and values, aligning with the AsyncStreamOutputChunk structure.
    """
    mock_session = MagicMock(spec=AioSession)
    mock_client = AsyncMock()

    async def fake_stream():
        yield {"content": "chunk1"}
        yield {"content": "chunk2"}

    mock_client.converse_stream = AsyncMock(
        return_value={
            "ResponseMetadata": {"request": "id"},
            "stream": fake_stream(),
        }
    )

    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = mock_client
    mock_context_manager.__aexit__.return_value = None
    mock_session.create_client.return_value = mock_context_manager

    wrapped_client = _AsyncBedrockRuntimeWrappedClient(mock_session, "test-model")

    chunks = []
    async for chunk in wrapped_client.converse_stream(param2="value2"):  # pyright: ignore [reportCallIssue]
        chunks.append(chunk)

    assert len(chunks) == 2

    for i, expected_content in enumerate(["chunk1", "chunk2"]):
        assert isinstance(chunks[i], dict)
        assert chunks[i]["model"] == "test-model"
        assert chunks[i]["content"] == expected_content
        assert chunks[i]["responseMetadata"] == {"request": "id"}

    mock_client.converse_stream.assert_called_once_with(param2="value2")

    mock_session.create_client.assert_called_once_with("bedrock-runtime")


@patch("mirascope.core.bedrock._utils._setup_call.Session")
@patch("mirascope.core.bedrock._utils._setup_call.get_session")
@patch("mirascope.core.bedrock._utils._setup_call._utils", new_callable=MagicMock)
def test_setup_call_env_vars(
    mock_utils: MagicMock,
    mock_get_session: MagicMock,
    mock_session_class: MagicMock,
    mock_base_setup_call: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that environment variables are properly passed to Session and get_session."""
    mock_utils.setup_call = mock_base_setup_call
    mock_base_setup_call.return_value[1] = [
        {"role": "user", "content": [{"text": "user test"}]},
    ]
    mock_base_setup_call.return_value[3] = {}

    # Set environment variables
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test_access_key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test_secret_key")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "test_session_token")
    monkeypatch.setenv("AWS_REGION_NAME", "us-west-2")
    monkeypatch.setenv("AWS_PROFILE", "test_profile")

    # Test sync client creation with env vars
    setup_call(
        model="anthropic.claude-v2",
        client=None,
        fn=MagicMock(),
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params={},
        response_model=None,
        stream=False,
    )

    # Verify Session was called with expected env vars
    mock_session_class.assert_called_once_with(
        aws_access_key_id="test_access_key",
        aws_secret_access_key="test_secret_key",
        aws_session_token="test_session_token",
        region_name="us-west-2",
        profile_name="test_profile",
    )

    # Test async client creation with env vars
    async def async_fn(): ...

    mock_session_class.reset_mock()

    setup_call(
        model="anthropic.claude-v2",
        client=None,
        fn=async_fn,
        fn_args={},
        dynamic_config=None,
        tools=None,
        json_mode=False,
        call_params={},
        response_model=None,
        stream=False,
    )

    # Verify get_session was called with expected env vars
    mock_get_session.assert_called_with(
        env_vars={
            "aws_access_key_id": "test_access_key",
            "aws_secret_access_key": "test_secret_key",
            "aws_session_token": "test_session_token",
            "region_name": "us-west-2",
            "profile_name": "test_profile",
        }
    )
