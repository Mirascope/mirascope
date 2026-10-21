"""Tests for MiniMaxProvider."""

import json
import os
from typing import get_args
from unittest.mock import patch

import httpx
import pytest

from mirascope import llm
from mirascope.llm.providers.minimax import MiniMaxModelId, MiniMaxProvider
from mirascope.llm.providers.minimax.model_id import (
    MINIMAX_KNOWN_MODELS,
    MiniMaxKnownModels,
    model_name,
)


def test_minimax_provider_initialization() -> None:
    """Test MiniMaxProvider initialization with api_key."""
    provider = MiniMaxProvider(api_key="test-api-key")
    assert provider.id == "minimax"
    assert provider.default_scope == "minimax/"


def test_minimax_provider_missing_api_key() -> None:
    """Test MiniMaxProvider raises error when API key is missing."""
    original_key = os.environ.pop("MINIMAX_API_KEY", None)
    try:
        with pytest.raises(ValueError) as exc_info:
            MiniMaxProvider()
        assert "MiniMax API key is required" in str(exc_info.value)
        assert "MINIMAX_API_KEY" in str(exc_info.value)
    finally:
        if original_key is not None:
            os.environ["MINIMAX_API_KEY"] = original_key


def test_minimax_provider_uses_env_var() -> None:
    """Test MiniMaxProvider uses MINIMAX_API_KEY from environment."""
    original_key = os.environ.get("MINIMAX_API_KEY")
    os.environ["MINIMAX_API_KEY"] = "env-test-key"
    try:
        provider = MiniMaxProvider()
        assert provider.id == "minimax"
    finally:
        if original_key is not None:
            os.environ["MINIMAX_API_KEY"] = original_key
        else:
            os.environ.pop("MINIMAX_API_KEY", None)


def test_minimax_provider_custom_base_url() -> None:
    """Test MiniMaxProvider with custom base_url."""
    provider = MiniMaxProvider(
        api_key="test-key", base_url="https://custom.minimax.io/v1"
    )
    assert provider.id == "minimax"


def test_minimax_provider_default_base_url() -> None:
    """Test MiniMaxProvider uses MiniMax API endpoint by default."""
    assert MiniMaxProvider.default_base_url == "https://api.minimax.io/v1"


def test_minimax_provider_call_strips_model_prefix() -> None:
    """The public call path passes the provider-specific model name to the SDK."""
    provider = MiniMaxProvider(api_key="test-key")
    with (
        patch.object(
            provider.client.chat.completions,
            "create",
            side_effect=RuntimeError("request captured"),
        ) as create,
        pytest.raises(RuntimeError, match="request captured"),
    ):
        provider.call(
            model_id="minimax/MiniMax-M2.7",
            messages=[llm.messages.user("Hello")],
            toolkit=llm.Toolkit([]),
        )
    assert create.call_args.kwargs["model"] == "MiniMax-M2.7"


def test_minimax_provider_api_key_required() -> None:
    """Test that api_key_required is True."""
    assert MiniMaxProvider.api_key_required is True


def test_minimax_provider_api_key_env_var() -> None:
    """Test that api_key_env_var is set correctly."""
    assert MiniMaxProvider.api_key_env_var == "MINIMAX_API_KEY"


def test_minimax_provider_name() -> None:
    """Test that provider_name is 'MiniMax'."""
    assert MiniMaxProvider.provider_name == "MiniMax"


def test_minimax_known_models_suggests_current_models() -> None:
    """Suggest Flash first without advertising legacy models."""
    assert get_args(MiniMaxKnownModels) == (
        "minimax/MiniMax-M3.1-Flash",
        "minimax/MiniMax-M3",
    )
    assert set(get_args(MiniMaxKnownModels)) == MINIMAX_KNOWN_MODELS


def test_minimax_model_name_helper_strips_prefix() -> None:
    """Test that model_name helper strips the 'minimax/' prefix."""
    assert model_name("minimax/MiniMax-M3") == "MiniMax-M3"
    assert model_name("minimax/MiniMax-M2.7") == "MiniMax-M2.7"


def test_minimax_model_name_helper_no_prefix() -> None:
    """Test that model_name helper passes through IDs without the prefix."""
    assert model_name("MiniMax-M3") == "MiniMax-M3"


def test_minimax_model_id_accepts_arbitrary_string() -> None:
    """Test that MiniMaxModelId accepts arbitrary strings (as `str` fallback)."""
    custom: MiniMaxModelId = "minimax/custom-future-model"
    assert custom == "minimax/custom-future-model"


@pytest.mark.parametrize(
    "model_id",
    [
        "minimax/MiniMax-M3.1-Flash",
        "minimax/MiniMax-M3",
        "minimax/MiniMax-M2.7",
        "minimax/MiniMax-M2.7-highspeed",
        "minimax/custom-future-model",
    ],
)
@pytest.mark.parametrize("base_url", [None, "https://custom.example/v1"])
def test_minimax_model_serializes_request(model_id: str, base_url: str | None) -> None:
    """Exercise registry dispatch and SDK serialization without network access."""
    requests: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "id": "test-completion",
                "object": "chat.completion",
                "created": 0,
                "model": model_name(model_id),
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Hello"},
                        "finish_reason": "stop",
                    }
                ],
            },
        )

    provider = MiniMaxProvider(api_key="test-key", base_url=base_url)
    llm.register_provider(provider)
    with (
        httpx.Client(transport=httpx.MockTransport(respond)) as client,
        patch.object(provider.client, "_client", client),
    ):
        response = llm.Model(model_id).call("Hello")
    assert response.model_id == model_id
    assert len(requests) == 1
    request = requests[0]
    assert str(request.url) == (
        f"{base_url or 'https://api.minimax.io/v1'}/chat/completions"
    )
    payload = json.loads(request.content)
    assert payload == {
        "model": model_name(model_id),
        "messages": [{"role": "user", "content": "Hello"}],
    }
