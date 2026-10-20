"""Offline API Route integration tests using the real OpenAI SDK."""

import json
import subprocess
import sys
from collections.abc import AsyncIterator
from typing import Literal

import httpx
import pytest
import pytest_asyncio
from pydantic import BaseModel

from mirascope import llm


@llm.tool
def get_weather(city: str) -> str:
    """Get the weather for a city."""
    return f"Sunny in {city}"


@llm.tool
async def get_weather_async(city: str) -> str:
    """Get the weather for a city asynchronously."""
    return f"Sunny in {city}"


class Answer(BaseModel):
    answer: str


@pytest.fixture
def requests() -> list[httpx.Request]:
    return []


@pytest_asyncio.fixture
async def provider(
    requests: list[httpx.Request],
) -> AsyncIterator[llm.providers.APIRouteProvider]:
    """Use mock transports for both SDK clients, never the network."""

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        body = json.loads(request.content)
        has_tools = bool(body.get("tools"))
        tool_calls = [
            {
                "id": "call_weather",
                "type": "function",
                "function": {
                    "name": body["tools"][0]["function"]["name"] if has_tools else "",
                    "arguments": '{"city":"Paris"}',
                },
            }
        ]
        finish_reason = "tool_calls" if has_tools else "stop"
        common = {"id": "chatcmpl-test", "created": 1, "model": body["model"]}
        usage = {"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8}

        if body.get("stream"):
            deltas = (
                [{"tool_calls": [{"index": 0, **tool_calls[0]}]}]
                if has_tools
                else [{"role": "assistant", "content": "Hello"}, {"content": "!"}]
            )
            chunks = [
                {
                    **common,
                    "object": "chat.completion.chunk",
                    "choices": [{"index": 0, "delta": delta, "finish_reason": None}],
                }
                for delta in deltas
            ]
            chunks.append(
                {
                    **common,
                    "object": "chat.completion.chunk",
                    "choices": [
                        {"index": 0, "delta": {}, "finish_reason": finish_reason}
                    ],
                    "usage": usage,
                }
            )
            content = "".join(f"data: {json.dumps(chunk)}\n\n" for chunk in chunks)
            return httpx.Response(
                200,
                headers={"content-type": "text/event-stream"},
                content=content + "data: [DONE]\n\n",
            )

        message = (
            {"role": "assistant", "content": None, "tool_calls": tool_calls}
            if has_tools
            else {"role": "assistant", "content": "Hello!"}
        )
        return httpx.Response(
            200,
            json={
                **common,
                "object": "chat.completion",
                "choices": [
                    {"index": 0, "message": message, "finish_reason": finish_reason}
                ],
                "usage": usage,
            },
        )

    provider = llm.providers.APIRouteProvider(api_key="test-api-route-key")
    provider.client.close()
    await provider.async_client.close()
    transport = httpx.MockTransport(respond)
    with httpx.Client(transport=transport) as client:
        async with httpx.AsyncClient(transport=transport) as async_client:
            provider.client = provider.client.with_options(http_client=client)
            provider.async_client = provider.async_client.with_options(
                http_client=async_client
            )
            llm.register_provider(provider, scope="api-route/")
            yield provider


def test_defaults() -> None:
    provider = llm.providers.APIRouteProvider(api_key="test-key")
    assert provider.id == "api-route"
    assert provider.default_scope == []
    assert "api-route" in llm.providers.KNOWN_PROVIDER_IDS
    assert isinstance(provider, llm.providers.BaseOpenAICompletionsProvider)
    assert str(provider.client.base_url) == "https://global.api-route.com/v1/"
    assert str(provider.async_client.base_url) == "https://global.api-route.com/v1/"


@pytest.mark.parametrize("explicit_key", [None, "explicit-key"])
def test_api_key_selection(
    monkeypatch: pytest.MonkeyPatch, explicit_key: str | None
) -> None:
    monkeypatch.setenv("API_ROUTE_API_KEY", "environment-key")
    monkeypatch.setenv("OPENAI_API_KEY", "unrelated-openai-key")
    provider = llm.providers.APIRouteProvider(api_key=explicit_key)
    assert provider.client.api_key == (explicit_key or "environment-key")
    assert provider.async_client.api_key == (explicit_key or "environment-key")


def test_missing_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("API_ROUTE_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "unrelated-openai-key")
    with pytest.raises(
        ValueError, match="API Route API key is required.*API_ROUTE_API_KEY"
    ):
        llm.providers.APIRouteProvider()


@pytest.mark.parametrize(
    ("model_id", "expected_model"),
    [
        ("api-route/gpt-4o", "gpt-4o"),
        ("api-route/anthropic/claude-sonnet-4-5", "anthropic/claude-sonnet-4-5"),
        ("api-route/openai/gpt-4o", "openai/gpt-4o"),
        ("api-route/vendor/model:variant", "vendor/model:variant"),
        ("openai/gpt-4o", "openai/gpt-4o"),
        ("vendor/api-route/model", "vendor/api-route/model"),
    ],
)
def test_model_name_on_wire(
    provider: llm.providers.APIRouteProvider,
    requests: list[httpx.Request],
    model_id: str,
    expected_model: str,
) -> None:
    llm.register_provider(provider, scope=model_id)
    response = llm.Model(model_id).call("Say hello")
    assert json.loads(requests[0].content)["model"] == expected_model
    assert response.model_id == model_id
    assert response.provider_model_name == expected_model


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["call", "call_async", "stream", "stream_async"])
@pytest.mark.parametrize("with_tools", [False, True])
async def test_call_paths(
    provider: llm.providers.APIRouteProvider,
    requests: list[httpx.Request],
    mode: Literal["call", "call_async", "stream", "stream_async"],
    with_tools: bool,
) -> None:
    model = llm.Model("api-route/gpt-4o", temperature=0.5, max_tokens=20)
    tools = [get_weather] if with_tools else None
    async_tools = [get_weather_async] if with_tools else None
    tool_name = "get_weather_async" if mode.endswith("_async") else "get_weather"
    if mode == "call":
        response = model.call("Say hello", tools=tools)
    elif mode == "call_async":
        response = await model.call_async("Say hello", tools=async_tools)
    elif mode == "stream":
        response = model.stream("Say hello", tools=tools)
        assert "".join(response.text_stream(sep="")) == ("" if with_tools else "Hello!")
    else:
        response = await model.stream_async("Say hello", tools=async_tools)
        assert "".join([text async for text in response.text_stream(sep="")]) == (
            "" if with_tools else "Hello!"
        )

    assert response.provider_id == provider.id
    assert response.model_id == "api-route/gpt-4o"
    assert response.provider_model_name == "gpt-4o"
    assert response.text() == ("" if with_tools else "Hello!")
    assert response.usage is not None
    assert response.usage.input_tokens == 5
    assert response.usage.output_tokens == 3
    assert response.tool_calls == (
        [llm.ToolCall(id="call_weather", name=tool_name, args='{"city":"Paris"}')]
        if with_tools
        else []
    )

    assert len(requests) == 1
    request = requests[0]
    assert request.method == "POST"
    assert str(request.url) == "https://global.api-route.com/v1/chat/completions"
    assert request.headers["authorization"] == "Bearer test-api-route-key"
    body = json.loads(request.content)
    assert body["model"] == "gpt-4o"
    assert body["messages"] == [{"role": "user", "content": "Say hello"}]
    assert body["temperature"] == 0.5
    assert body["max_tokens"] == 20
    if with_tools:
        assert body["tools"][0]["function"]["name"] == tool_name
    if mode in ("stream", "stream_async"):
        assert body["stream"] is True
        assert body["stream_options"] == {"include_usage": True}


@pytest.mark.parametrize(
    ("model", "reasoning"),
    [
        ("gpt-4o", False),
        ("gpt-5", True),
        ("o1", True),
        ("o3-mini", True),
        ("o4-mini", True),
        ("claude-sonnet-4-5", False),
        ("vendor/custom-model", False),
        ("openai/o3", False),
    ],
)
def test_model_feature_encoding(
    provider: llm.providers.APIRouteProvider,
    requests: list[httpx.Request],
    model: str,
    reasoning: bool,
) -> None:
    llm.Model(f"api-route/{model}", temperature=0.5, max_tokens=20).call("Hello")
    body = json.loads(requests[0].content)
    assert ("temperature" not in body) is reasoning
    if reasoning:
        assert body["max_completion_tokens"] == 20
        assert "max_tokens" not in body
    else:
        assert body["temperature"] == 0.5
        assert body["max_tokens"] == 20
        assert "max_completion_tokens" not in body


@pytest.mark.parametrize(
    ("model", "strict"),
    [("gpt-4o", True), ("gpt-4o-2024-05-13", False), ("claude-sonnet-4-5", False)],
)
def test_model_format_defaults(
    provider: llm.providers.APIRouteProvider,
    requests: list[httpx.Request],
    model: str,
    strict: bool,
) -> None:
    llm.Model(f"api-route/{model}").call("Hello", format=Answer)
    body = json.loads(requests[0].content)
    if strict:
        assert body["response_format"]["type"] == "json_schema"
        assert body["response_format"]["json_schema"]["strict"] is True
    else:
        assert "response_format" not in body
        assert body["tools"]


def test_auto_registration_is_scoped(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_ROUTE_API_KEY", "test-key")
    provider = llm.providers.get_provider_for_model("api-route/gpt-4o")
    assert isinstance(provider, llm.providers.APIRouteProvider)
    assert (
        llm.providers.get_provider_for_model("api-route/claude-sonnet-4-5") is provider
    )
    assert llm.providers.get_provider_for_model("openai/gpt-4o") is not provider
    assert (
        llm.providers.get_provider_for_model("anthropic/claude-sonnet-4-5")
        is not provider
    )
    with pytest.raises(llm.NoRegisteredProviderError):
        llm.providers.get_provider_for_model("gpt-4o")


def test_explicit_registration_and_custom_base_url() -> None:
    provider = llm.register_provider(
        "api-route",
        scope=["openai/", "anthropic/"],
        api_key="custom-key",
        base_url="https://example.com/v1",
    )
    assert isinstance(provider, llm.providers.APIRouteProvider)
    assert llm.providers.get_provider_for_model("openai/gpt-4o") is provider
    assert (
        llm.providers.get_provider_for_model("anthropic/claude-sonnet-4-5") is provider
    )
    assert str(provider.client.base_url) == "https://example.com/v1/"
    assert str(provider.async_client.base_url) == "https://example.com/v1/"
    assert provider.client.api_key == "custom-key"
    assert provider.async_client.api_key == "custom-key"


def test_default_registration_does_not_take_over_scopes() -> None:
    provider = llm.register_provider("api-route", api_key="explicit-key")
    assert llm.providers.get_provider_for_model("api-route/gpt-4o") is not provider
    assert llm.providers.get_provider_for_model("openai/gpt-4o") is not provider
    with pytest.raises(llm.NoRegisteredProviderError):
        llm.providers.get_provider_for_model("gpt-4o")


def test_auto_registration_missing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("API_ROUTE_API_KEY", raising=False)
    with pytest.raises(llm.MissingAPIKeyError) as exc_info:
        llm.providers.get_provider_for_model("api-route/gpt-4o")
    assert exc_info.value.provider_id == "api-route"
    assert exc_info.value.env_var == "API_ROUTE_API_KEY"
    assert "MIRASCOPE_API_KEY" not in str(exc_info.value)


def test_missing_openai_dependency() -> None:
    """Import in a fresh process so dependency stubbing cannot leak to other tests."""
    script = """
import sys

# Block the optional dependency before importing the public API.
sys.modules["openai"] = None
from mirascope import llm

try:
    llm.providers.APIRouteProvider(api_key="unused-test-key")
except ImportError as error:
    message = str(error)
    assert "APIRouteProvider" in message
    assert "mirascope[openai]" in message
else:
    raise AssertionError("Missing OpenAI dependency should fail on provider creation")
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
