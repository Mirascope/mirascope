"""Tests for BedrockBoto3Provider - error cases only.

Normal operation is tested via E2E tests with VCR cassettes in
tests/e2e/input/test_openai_compatibility_providers.py
"""

from __future__ import annotations

import builtins
import importlib
import sys
from types import ModuleType
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import BotoCoreError, ClientError
from pydantic import BaseModel

from mirascope import llm
from mirascope.llm.providers.bedrock.boto3 import (
    BedrockBoto3Provider,
)

EMPTY_TOOLKIT = llm.Toolkit(None)


@llm.tool(strict=True)
def strict_tool() -> str:
    """A strict test tool."""
    return "result"


def _make_provider(
    mock_session_cls: MagicMock,
) -> tuple[BedrockBoto3Provider, MagicMock]:
    mock_client = MagicMock()
    mock_session = MagicMock()
    mock_session.client.return_value = mock_client
    mock_session_cls.return_value = mock_session
    provider = BedrockBoto3Provider()
    return provider, mock_client


@patch("boto3.Session")
def test_call_raises_for_strict_tools(mock_session_cls: MagicMock) -> None:
    provider, _ = _make_provider(mock_session_cls)

    with pytest.raises(llm.FeatureNotSupportedError, match="strict tools"):
        provider.call(
            model_id="bedrock/amazon.nova-micro-v1:0",
            messages=[llm.messages.user("hello")],
            toolkit=llm.Toolkit([strict_tool]),
        )


@patch("boto3.Session")
def test_call_raises_for_strict_format(mock_session_cls: MagicMock) -> None:
    provider, _ = _make_provider(mock_session_cls)

    class TestFormat(BaseModel):
        value: str

    strict_format = llm.format(TestFormat, mode="strict")

    with pytest.raises(llm.FeatureNotSupportedError, match="strict"):
        provider.call(
            model_id="bedrock/amazon.nova-micro-v1:0",
            messages=[llm.messages.user("hello")],
            toolkit=EMPTY_TOOLKIT,
            format=strict_format,
        )


@patch("boto3.Session")
def test_call_raises_for_url_image(mock_session_cls: MagicMock) -> None:
    provider, _ = _make_provider(mock_session_cls)
    image = llm.Image(
        source=llm.URLImageSource(
            type="url_image_source",
            url="https://example.com/image.png",
        )
    )

    with pytest.raises(llm.FeatureNotSupportedError, match="URL image sources"):
        provider.call(
            model_id="bedrock/amazon.nova-micro-v1:0",
            messages=[llm.messages.user([image])],
            toolkit=EMPTY_TOOLKIT,
        )


@patch("boto3.Session")
def test_call_raises_for_audio(mock_session_cls: MagicMock) -> None:
    provider, _ = _make_provider(mock_session_cls)
    audio = llm.Audio(
        source=llm.Base64AudioSource(
            type="base64_audio_source",
            mime_type="audio/mp3",
            data="base64data",
        )
    )

    with pytest.raises(llm.FeatureNotSupportedError, match="audio input"):
        provider.call(
            model_id="bedrock/amazon.nova-micro-v1:0",
            messages=[llm.messages.user([audio])],
            toolkit=EMPTY_TOOLKIT,
        )


@patch("boto3.Session")
def test_call_raises_for_document(mock_session_cls: MagicMock) -> None:
    provider, _ = _make_provider(mock_session_cls)
    doc = llm.Document(
        source=llm.content.Base64DocumentSource(
            type="base64_document_source",
            data="dGVzdA==",
            media_type="application/pdf",
        )
    )

    with pytest.raises(
        llm.FeatureNotSupportedError, match="document support is not implemented"
    ):
        provider.call(
            model_id="bedrock/amazon.nova-micro-v1:0",
            messages=[llm.messages.user([doc])],
            toolkit=EMPTY_TOOLKIT,
        )


@pytest.mark.parametrize(
    ("code", "expected_error"),
    [
        ("ThrottlingException", llm.RateLimitError),
        ("AccessDeniedException", llm.PermissionError),
        ("ValidationException", llm.BadRequestError),
        ("ResourceNotFoundException", llm.NotFoundError),
        ("ServiceUnavailableException", llm.ServerError),
        ("ModelNotReadyException", llm.ServerError),
        ("InternalServerException", llm.ServerError),
    ],
)
@patch("boto3.Session")
def test_call_maps_client_errors(
    mock_session_cls: MagicMock,
    code: str,
    expected_error: type[llm.ProviderError],
) -> None:
    provider, mock_client = _make_provider(mock_session_cls)
    mock_client.converse.side_effect = ClientError(
        error_response={"Error": {"Code": code, "Message": "boom"}},
        operation_name="converse",
    )

    with pytest.raises(expected_error):
        provider.call(
            model_id="bedrock/amazon.titan-text-express-v1",
            messages=[llm.messages.user("hello")],
            toolkit=EMPTY_TOOLKIT,
        )


@patch("boto3.Session")
def test_call_maps_unknown_client_error(mock_session_cls: MagicMock) -> None:
    provider, mock_client = _make_provider(mock_session_cls)
    mock_client.converse.side_effect = ClientError(
        error_response={"Error": {"Code": "UnknownException", "Message": "boom"}},
        operation_name="converse",
    )

    with pytest.raises(llm.ProviderError):
        provider.call(
            model_id="bedrock/amazon.titan-text-express-v1",
            messages=[llm.messages.user("hello")],
            toolkit=EMPTY_TOOLKIT,
        )


@patch("boto3.Session")
def test_call_maps_botocore_error(mock_session_cls: MagicMock) -> None:
    provider, mock_client = _make_provider(mock_session_cls)
    mock_client.converse.side_effect = BotoCoreError()

    with pytest.raises(llm.ProviderError):
        provider.call(
            model_id="bedrock/amazon.titan-text-express-v1",
            messages=[llm.messages.user("hello")],
            toolkit=EMPTY_TOOLKIT,
        )


@patch("boto3.Session")
def test_provider_init_with_aws_profile(mock_session_cls: MagicMock) -> None:
    mock_client = MagicMock()
    mock_session = MagicMock()
    mock_session.client.return_value = mock_client
    mock_session_cls.return_value = mock_session

    BedrockBoto3Provider(aws_profile="test-profile")

    mock_session_cls.assert_called_once()
    session_kwargs = mock_session_cls.call_args[1]
    assert session_kwargs["profile_name"] == "test-profile"


@patch("boto3.Session")
def test_provider_init_with_all_credentials(mock_session_cls: MagicMock) -> None:
    mock_client = MagicMock()
    mock_session = MagicMock()
    mock_session.client.return_value = mock_client
    mock_session_cls.return_value = mock_session

    BedrockBoto3Provider(
        aws_access_key="access-key",
        aws_secret_key="secret-key",
        aws_session_token="session-token",
        base_url="https://custom-endpoint.example.com",
    )

    client_kwargs = mock_session.client.call_args[1]
    assert client_kwargs["aws_access_key_id"] == "access-key"
    assert client_kwargs["aws_secret_access_key"] == "secret-key"
    assert client_kwargs["aws_session_token"] == "session-token"
    assert client_kwargs["endpoint_url"] == "https://custom-endpoint.example.com"


@patch("boto3.Session")
def test_get_error_status_returns_none_without_response(
    mock_session_cls: MagicMock,
) -> None:
    provider, _ = _make_provider(mock_session_cls)
    error = Exception("error without response")
    assert provider.get_error_status(error) is None


@patch("boto3.Session")
@pytest.mark.asyncio
async def test_stream_async_propagates_errors(mock_session_cls: MagicMock) -> None:
    provider, mock_client = _make_provider(mock_session_cls)

    def raise_during_iteration(**_kwargs: Any) -> dict[str, Any]:  # noqa: ANN401
        def failing_stream() -> Any:  # noqa: ANN401
            yield {"contentBlockStart": {"start": {}}}
            raise ClientError(
                error_response={
                    "Error": {"Code": "ThrottlingException", "Message": "boom"}
                },
                operation_name="converse_stream",
            )

        return {"stream": failing_stream()}

    mock_client.converse_stream.side_effect = raise_during_iteration

    stream = await provider.stream_async(
        model_id="bedrock/amazon.nova-micro-v1:0",
        messages=[llm.messages.user("hello")],
        toolkit=llm.AsyncToolkit(None),
    )
    with pytest.raises(llm.RateLimitError):
        async for _ in stream.chunk_stream():
            pass


def test_boto3_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test BedrockBoto3Provider raises ImportError when boto3 is unavailable."""
    modules_to_remove = [
        "mirascope.llm.providers.bedrock.boto3.provider",
        "mirascope.llm.providers.bedrock.boto3",
    ]
    original_modules = {name: sys.modules.get(name) for name in modules_to_remove}
    for name in modules_to_remove:
        sys.modules.pop(name, None)

    original_import = builtins.__import__

    def mock_import(name: str, *args: Any, **kwargs: Any) -> ModuleType:  # noqa: ANN401
        if name == "boto3" or name.startswith("boto3."):
            raise ImportError(f"No module named '{name}'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

    try:
        provider_module = importlib.import_module(
            "mirascope.llm.providers.bedrock.boto3.provider"
        )

        with pytest.raises(ImportError, match="bedrock"):
            provider_module.BedrockBoto3Provider()
    finally:
        for name, module in original_modules.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module
