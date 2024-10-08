from unittest.mock import MagicMock, patch

import pytest
from mypy_boto3_bedrock_runtime import BedrockRuntimeClient
from types_aiobotocore_bedrock_runtime import (
    BedrockRuntimeClient as AsyncBedrockRuntimeClient,
)

from mirascope.core.bedrock._utils._get_client import (
    _get_async_client,
    _get_sync_client,
)


@patch("mirascope.core.bedrock._utils._get_client.Session")
def test_get_sync_client(mock_session):
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance

    mock_client = MagicMock(spec=BedrockRuntimeClient)
    mock_session_instance.client.return_value = mock_client

    client = _get_sync_client()

    assert isinstance(client, MagicMock)
    assert client == mock_client
    mock_session.assert_called_once()
    mock_session_instance.client.assert_called_once_with("bedrock-runtime")


@pytest.mark.asyncio
@patch("mirascope.core.bedrock._utils._get_client.get_session")
async def test_get_async_client(mock_get_session):
    mock_session = MagicMock()
    mock_get_session.return_value = mock_session

    mock_client = MagicMock(spec=AsyncBedrockRuntimeClient)
    mock_session.create_client.return_value.__aenter__.return_value = mock_client

    client = await _get_async_client()

    assert isinstance(client, MagicMock)
    assert client == mock_client
    mock_get_session.assert_called_once()
    mock_session.create_client.assert_called_once_with("bedrock-runtime")
