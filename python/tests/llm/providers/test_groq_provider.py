"""Tests for GroqProvider."""

import json
from collections.abc import Iterator

import httpx
import pytest

from mirascope import llm
from mirascope.llm.providers.groq import GroqProvider
from mirascope.llm.providers.openai.completions._utils import (
    CompletionsModelFeatureInfo,
)


class _InspectableGroqProvider(GroqProvider):
    def model_name(self, model_id: str) -> str:
        return self._model_name(model_id)

    def model_feature_info(self, model_id: str) -> CompletionsModelFeatureInfo:
        return self._model_feature_info(model_id)


def test_groq_provider_initialization() -> None:
    """Test GroqProvider initialization with api_key."""
    provider = GroqProvider(api_key="test-api-key")
    assert provider.id == "groq"
    assert provider.default_scope == "groq/"
    assert "groq" in llm.providers.KNOWN_PROVIDER_IDS
    assert isinstance(provider, llm.providers.BaseOpenAICompletionsProvider)


def test_groq_provider_missing_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test GroqProvider raises error when API key is missing."""
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(ValueError) as exc_info:
        GroqProvider()
    assert "Groq API key is required" in str(exc_info.value)
    assert "GROQ_API_KEY" in str(exc_info.value)


def test_groq_provider_uses_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test GroqProvider uses GROQ_API_KEY from environment."""
    monkeypatch.setenv("GROQ_API_KEY", "env-test-key")
    provider = GroqProvider()
    assert provider.client.api_key == "env-test-key"
    assert provider.async_client.api_key == "env-test-key"


def test_groq_provider_default_base_url() -> None:
    """Test GroqProvider uses Groq's OpenAI-compatible endpoint by default."""
    provider = GroqProvider(api_key="test-key")
    assert str(provider.client.base_url) == "https://api.groq.com/openai/v1/"
    assert str(provider.async_client.base_url) == "https://api.groq.com/openai/v1/"


def test_groq_provider_custom_base_url() -> None:
    """Test GroqProvider with custom base_url."""
    provider = GroqProvider(api_key="test-key", base_url="https://example.com/v1")
    assert str(provider.client.base_url) == "https://example.com/v1/"
    assert str(provider.async_client.base_url) == "https://example.com/v1/"


def test_groq_provider_model_name() -> None:
    """Test GroqProvider strips only the 'groq/' prefix from model_id."""
    provider = _InspectableGroqProvider(api_key="test-key")
    assert (
        provider.model_name("groq/llama-3.3-70b-versatile") == "llama-3.3-70b-versatile"
    )
    assert provider.model_name("groq/openai/gpt-oss-120b") == "openai/gpt-oss-120b"
    assert (
        provider.model_name("groq/moonshotai/kimi-k2-instruct")
        == "moonshotai/kimi-k2-instruct"
    )
    assert provider.model_name("llama-3.1-8b-instant") == "llama-3.1-8b-instant"


def test_groq_provider_model_feature_info_is_empty() -> None:
    """Test Groq models never inherit OpenAI API feature info.

    `openai/gpt-oss-*` on Groq are open-weight models, not OpenAI API models,
    so OpenAI-specific assumptions (audio, reasoning params) must not apply.
    """
    provider = _InspectableGroqProvider(api_key="test-key")
    assert (
        provider.model_feature_info("groq/openai/gpt-oss-120b")
        == CompletionsModelFeatureInfo()
    )
    assert (
        provider.model_feature_info("groq/llama-3.3-70b-versatile")
        == CompletionsModelFeatureInfo()
    )


def test_groq_scope_auto_registers(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test 'groq/' model IDs auto-register GroqProvider when GROQ_API_KEY is set."""
    monkeypatch.setenv("GROQ_API_KEY", "env-test-key")
    provider = llm.providers.get_provider_for_model("groq/llama-3.3-70b-versatile")
    assert isinstance(provider, GroqProvider)


def test_groq_scope_missing_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test 'groq/' model IDs raise MissingAPIKeyError without GROQ_API_KEY."""
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(llm.MissingAPIKeyError) as exc_info:
        llm.providers.get_provider_for_model("groq/llama-3.3-70b-versatile")
    assert exc_info.value.provider_id == "groq"
    assert exc_info.value.env_var == "GROQ_API_KEY"


@pytest.fixture
def requests() -> list[httpx.Request]:
    return []


@pytest.fixture
def mocked_provider(requests: list[httpx.Request]) -> Iterator[GroqProvider]:
    """GroqProvider whose sync client is served by a mock transport, never the network."""

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        body = json.loads(request.content)
        common = {"id": "chatcmpl-test", "created": 1, "model": body["model"]}
        usage = {"prompt_tokens": 5, "completion_tokens": 2, "total_tokens": 7}
        if body.get("stream"):
            chunks = [
                {
                    **common,
                    "object": "chat.completion.chunk",
                    "choices": [
                        {
                            "index": 0,
                            "delta": {"role": "assistant", "content": "Hello!"},
                            "finish_reason": None,
                        }
                    ],
                },
                {
                    **common,
                    "object": "chat.completion.chunk",
                    "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
                    "usage": usage,
                },
            ]
            content = "".join(f"data: {json.dumps(chunk)}\n\n" for chunk in chunks)
            return httpx.Response(
                200,
                headers={"content-type": "text/event-stream"},
                content=content + "data: [DONE]\n\n",
            )
        return httpx.Response(
            200,
            json={
                **common,
                "object": "chat.completion",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Hello!"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": usage,
            },
        )

    provider = GroqProvider(api_key="test-groq-key")
    provider.client.close()
    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        provider.client = provider.client.with_options(http_client=client)
        llm.register_provider(provider)
        yield provider


def test_groq_call_sends_groq_model_name(
    mocked_provider: GroqProvider, requests: list[httpx.Request]
) -> None:
    """Test a call hits Groq's chat completions endpoint with the stripped model name."""
    response = llm.Model("groq/openai/gpt-oss-120b").call(
        [llm.messages.user("Say hello")]
    )

    assert response.text() == "Hello!"
    assert response.provider_id == "groq"
    assert response.model_id == "groq/openai/gpt-oss-120b"
    assert response.provider_model_name == "openai/gpt-oss-120b"
    assert response.usage is not None
    assert response.usage.input_tokens == 5
    assert response.usage.output_tokens == 2

    (request,) = requests
    assert str(request.url) == "https://api.groq.com/openai/v1/chat/completions"
    assert request.headers["authorization"] == "Bearer test-groq-key"
    body = json.loads(request.content)
    assert body["model"] == "openai/gpt-oss-120b"
    assert body["messages"] == [{"role": "user", "content": "Say hello"}]


def test_groq_stream_sends_groq_model_name(
    mocked_provider: GroqProvider, requests: list[httpx.Request]
) -> None:
    """Test a streamed call is decoded and requests usage from Groq."""
    response = llm.Model("groq/llama-3.3-70b-versatile").stream(
        [llm.messages.user("Say hello")]
    )
    response.finish()

    assert response.text() == "Hello!"
    assert response.provider_model_name == "llama-3.3-70b-versatile"
    assert response.usage is not None
    assert response.usage.input_tokens == 5

    (request,) = requests
    body = json.loads(request.content)
    assert body["model"] == "llama-3.3-70b-versatile"
    assert body["stream"] is True
    assert body["stream_options"] == {"include_usage": True}
