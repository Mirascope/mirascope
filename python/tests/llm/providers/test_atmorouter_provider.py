"""Tests for AtmoRouterProvider."""

import json
import os

import httpx
import pytest

from mirascope import llm
from mirascope.llm.providers.atmorouter.provider import AtmoRouterProvider
from mirascope.llm.providers.openai.completions._utils import (
    CompletionsModelFeatureInfo,
)


class _InspectableAtmoRouterProvider(AtmoRouterProvider):
    def model_name(self, model_id: str) -> str:
        return self._model_name(model_id)

    def model_feature_info(self, model_id: str) -> CompletionsModelFeatureInfo:
        return self._model_feature_info(model_id)


def test_atmorouter_provider_initialization() -> None:
    """Test AtmoRouterProvider initialization with api_key."""
    provider = _InspectableAtmoRouterProvider(api_key="test-api-key")
    assert provider.id == "atmorouter"
    assert provider.default_scope == []


def test_atmorouter_provider_requires_api_key() -> None:
    """Test AtmoRouterProvider raises error when API key is missing."""
    original_key = os.environ.pop("ATMOROUTER_API_KEY", None)
    try:
        with pytest.raises(ValueError) as exc_info:
            AtmoRouterProvider()
        assert "AtmoRouter API key is required" in str(exc_info.value)
        assert "ATMOROUTER_API_KEY" in str(exc_info.value)
    finally:
        if original_key is not None:
            os.environ["ATMOROUTER_API_KEY"] = original_key


def test_atmorouter_provider_uses_env_api_key() -> None:
    """Test AtmoRouterProvider uses ATMOROUTER_API_KEY from environment."""
    original_key = os.environ.get("ATMOROUTER_API_KEY")
    os.environ["ATMOROUTER_API_KEY"] = "env-test-key"
    try:
        provider = _InspectableAtmoRouterProvider()
        assert provider.client.api_key == "env-test-key"
    finally:
        if original_key is not None:
            os.environ["ATMOROUTER_API_KEY"] = original_key
        else:
            os.environ.pop("ATMOROUTER_API_KEY", None)


def test_atmorouter_provider_default_base_url() -> None:
    """Test AtmoRouterProvider uses the AtmoRouter API by default."""
    provider = _InspectableAtmoRouterProvider(api_key="test-key")
    assert str(provider.client.base_url) == "https://atmorouter.dev/v1/"
    assert str(provider.async_client.base_url) == "https://atmorouter.dev/v1/"


def test_atmorouter_provider_custom_base_url() -> None:
    """Test AtmoRouterProvider with custom base_url."""
    provider = _InspectableAtmoRouterProvider(
        api_key="test-key", base_url="https://example.com/v1"
    )
    assert provider.id == "atmorouter"
    assert str(provider.client.base_url) == "https://example.com/v1/"


def test_atmorouter_model_name() -> None:
    """Test AtmoRouterProvider strips only the 'atmorouter/' prefix."""
    provider = _InspectableAtmoRouterProvider(api_key="test-key")
    assert (
        provider.model_name("atmorouter/cc/claude-sonnet-4-6") == "cc/claude-sonnet-4-6"
    )
    assert (
        provider.model_name("atmorouter/atmo/deepseek-v4.1-flash")
        == "atmo/deepseek-v4.1-flash"
    )
    assert provider.model_name("cc/claude-sonnet-4-6") == "cc/claude-sonnet-4-6"


def test_atmorouter_model_feature_info() -> None:
    """Test AtmoRouter models use empty (permissive) feature info."""
    provider = _InspectableAtmoRouterProvider(api_key="test-key")
    info = provider.model_feature_info("atmorouter/cc/claude-sonnet-4-6")
    assert info == CompletionsModelFeatureInfo()


def test_atmorouter_auto_registers_scope() -> None:
    """Test 'atmorouter/' models resolve to AtmoRouterProvider automatically."""
    provider = llm.providers.get_provider_for_model("atmorouter/cc/claude-sonnet-4-6")
    assert isinstance(provider, AtmoRouterProvider)


def test_atmorouter_call_sends_model_without_scope() -> None:
    """Test a call hits /chat/completions with the AtmoRouter model ID."""
    requests: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        body = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "id": "chatcmpl-test",
                "object": "chat.completion",
                "created": 1,
                "model": body["model"],
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Hello!"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 5,
                    "completion_tokens": 2,
                    "total_tokens": 7,
                },
            },
        )

    provider = AtmoRouterProvider(api_key="test-key")
    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        provider.client = provider.client.with_options(http_client=client)
        response = provider.call(
            model_id="atmorouter/cc/claude-sonnet-4-6",
            messages=[llm.messages.user("Hello")],
            toolkit=llm.Toolkit([]),
        )

    assert response.text() == "Hello!"
    assert response.provider_id == "atmorouter"
    assert len(requests) == 1
    assert str(requests[0].url) == "https://atmorouter.dev/v1/chat/completions"
    assert requests[0].headers["authorization"] == "Bearer test-key"
    assert json.loads(requests[0].content)["model"] == "cc/claude-sonnet-4-6"
