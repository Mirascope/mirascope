"""Tests for BedrockOpenAIProvider."""

from pathlib import Path

import pytest

from mirascope.llm.providers.bedrock._utils import BEDROCK_OPENAI_MODEL_PREFIXES
from mirascope.llm.providers.bedrock.openai import BedrockOpenAIProvider
from mirascope.llm.providers.bedrock.openai.provider import (
    BedrockOpenAIRoutedProvider,
    _build_bedrock_openai_base_url,  # pyright: ignore[reportPrivateUsage]
)


def test_build_bedrock_openai_base_url() -> None:
    """Test _build_bedrock_openai_base_url constructs correct URL."""
    url = _build_bedrock_openai_base_url("us-east-1")
    assert url == "https://bedrock-runtime.us-east-1.amazonaws.com/openai/v1"


def test_build_bedrock_openai_base_url_other_region() -> None:
    """Test _build_bedrock_openai_base_url with different region."""
    url = _build_bedrock_openai_base_url("eu-west-1")
    assert url == "https://bedrock-runtime.eu-west-1.amazonaws.com/openai/v1"


def test_bedrock_openai_model_prefixes() -> None:
    """Test BEDROCK_OPENAI_MODEL_PREFIXES contains OpenAI prefix."""
    assert "bedrock/openai." in BEDROCK_OPENAI_MODEL_PREFIXES


def test_bedrock_openai_provider_requires_credentials(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Test BedrockOpenAIProvider raises error without credentials."""
    monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)
    monkeypatch.delenv("AWS_BEARER_TOKEN_BEDROCK", raising=False)
    monkeypatch.setenv("AWS_EC2_METADATA_DISABLED", "true")
    credentials_file = tmp_path / "credentials"
    config_file = tmp_path / "config"
    credentials_file.write_text("")
    config_file.write_text("")
    monkeypatch.setenv("AWS_SHARED_CREDENTIALS_FILE", str(credentials_file))
    monkeypatch.setenv("AWS_CONFIG_FILE", str(config_file))
    with pytest.raises(
        ValueError, match="requires either an API key or AWS credentials"
    ):
        BedrockOpenAIProvider(aws_region="us-east-1")


def test_bedrock_openai_provider_default_scope() -> None:
    """Test BedrockOpenAIProvider has correct default scope."""
    assert BedrockOpenAIProvider.default_scope == "bedrock/openai."


def test_bedrock_openai_provider_id() -> None:
    """Test BedrockOpenAIProvider has correct provider id."""
    assert BedrockOpenAIProvider.id == "bedrock:openai"


def test_bedrock_openai_routed_provider_id() -> None:
    """Test BedrockOpenAIRoutedProvider reports provider_id as bedrock."""
    assert BedrockOpenAIRoutedProvider.id == "bedrock"


def test_bedrock_openai_provider_get_error_status() -> None:
    """Test BedrockOpenAIProvider.get_error_status extracts status code."""
    provider = BedrockOpenAIProvider(
        api_key="test-api-key",
        base_url="https://example.com/openai/v1",
    )

    class MockError(Exception):
        status_code = 429

    assert provider.get_error_status(MockError()) == 429
    assert provider.get_error_status(Exception()) is None
