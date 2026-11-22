"""Tests for TogetherProvider."""

import os
from unittest.mock import patch

import pytest

from mirascope import llm
from mirascope.llm.providers.together.provider import TogetherProvider


def test_together_provider_initialization() -> None:
    """Test TogetherProvider initialization with api_key."""
    provider = TogetherProvider(api_key="test-api-key")
    assert provider.id == "together"
    assert provider.default_scope == []


def test_together_provider_missing_api_key() -> None:
    """Test TogetherProvider raises error when API key is missing."""
    original_key = os.environ.pop("TOGETHER_API_KEY", None)
    try:
        with pytest.raises(ValueError) as exc_info:
            TogetherProvider()
        assert "Together API key is required" in str(exc_info.value)
        assert "TOGETHER_API_KEY" in str(exc_info.value)
    finally:
        if original_key is not None:
            os.environ["TOGETHER_API_KEY"] = original_key


def test_together_provider_uses_env_var() -> None:
    """Test TogetherProvider uses TOGETHER_API_KEY from environment."""
    original_key = os.environ.get("TOGETHER_API_KEY")
    os.environ["TOGETHER_API_KEY"] = "env-test-key"
    try:
        provider = TogetherProvider()
        assert provider.id == "together"
    finally:
        if original_key is not None:
            os.environ["TOGETHER_API_KEY"] = original_key
        else:
            os.environ.pop("TOGETHER_API_KEY", None)


def test_together_provider_custom_base_url() -> None:
    """Test TogetherProvider with custom base_url."""
    provider = TogetherProvider(
        api_key="test-key", base_url="https://custom.together.xyz/v1"
    )
    assert provider.id == "together"


@pytest.mark.parametrize(
    "model_id",
    [
        "together/meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    ],
)
def test_together_provider_model_name(model_id: str) -> None:
    """The public call sends the model name without Mirascope's prefix."""
    provider = TogetherProvider(api_key="test-key")
    with (
        patch.object(
            provider.client.chat.completions,
            "create",
            side_effect=RuntimeError("request captured"),
        ) as create,
        pytest.raises(RuntimeError, match="request captured"),
    ):
        provider.call(
            model_id=model_id,
            messages=[llm.messages.user("Hello")],
            toolkit=llm.Toolkit([]),
        )
    assert create.call_args.kwargs["model"] == (
        "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    )
