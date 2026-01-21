"""End-to-end tests for Mirascope Router provider."""

import os

import pytest

from mirascope import llm
from tests.utils import (
    Snapshot,
    snapshot_test,
)

MIRASCOPE_MODEL_IDS = [
    "openai/gpt-5-mini",
    "openai/gpt-5-mini:completions",
    "openai/gpt-5-mini:responses",
    "anthropic/claude-haiku-4-5",
    "google/gemini-2.5-flash",
]


@pytest.mark.parametrize("model_id", MIRASCOPE_MODEL_IDS)
@pytest.mark.vcr
def test_mirascope_provider(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test that Mirascope Router provider works correctly."""

    @llm.call(model_id)
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    llm.register_provider(
        "mirascope",
        base_url="http://localhost:3000/router/v2",
    )

    model_scope, model_name = model_id.split("/", 1)

    with snapshot_test(snapshot) as snap:
        response = add_numbers(4200, 42)
        assert response.provider_id == model_scope
        assert model_name in response.provider_model_name
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )


@pytest.mark.parametrize("model_id", MIRASCOPE_MODEL_IDS)
@pytest.mark.vcr
def test_mirascope_provider_streaming(
    model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test that Mirascope Router provider works correctly with streaming."""

    @llm.call(model_id)
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    llm.register_provider(
        "mirascope",
        base_url="http://localhost:3000/router/v2",
    )

    model_scope, model_name = model_id.split("/", 1)

    with snapshot_test(snapshot) as snap:
        stream = add_numbers.stream(4200, 42)
        assert stream.provider_id == model_scope
        assert model_name in stream.provider_model_name

        stream.finish()
        content = stream.pretty()

        snap.set_response(stream)
        assert "4242" in content, f"Expected '4242' in streamed content: {content}"


def test_mirascope_provider_missing_api_key() -> None:
    """Test that Mirascope provider raises clear error when API key is missing."""
    original_key = os.environ.pop("MIRASCOPE_API_KEY", None)
    try:
        with pytest.raises(ValueError) as exc_info:
            llm.providers.MirascopeProvider()
        assert "Mirascope API key not found" in str(exc_info.value)
        assert "MIRASCOPE_API_KEY" in str(exc_info.value)
    finally:
        if original_key is not None:
            os.environ["MIRASCOPE_API_KEY"] = original_key
