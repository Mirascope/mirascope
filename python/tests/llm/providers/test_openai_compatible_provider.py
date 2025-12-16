"""Tests for BaseOpenAICompletionsProvider internals."""

import os
from unittest.mock import MagicMock, patch

import pytest

from mirascope.llm.providers.openai.completions.base_provider import (
    BaseOpenAICompletionsProvider,
)


class _DummyProvider(BaseOpenAICompletionsProvider):
    """Minimal provider for testing BaseOpenAICompletionsProvider behavior."""

    id = "dummy:completions"
    default_scope = "dummy/"
    default_base_url = None
    api_key_env_var = "DUMMY_API_KEY"
    api_key_required = True

    def _model_name(self, model_id: str) -> str:
        return "dummy-model"


class _KeylessProvider(BaseOpenAICompletionsProvider):
    """Provider that doesn't require an API key but has a default base URL."""

    id = "keyless"
    default_scope = "keyless/"
    default_base_url = "https://example.com"
    api_key_env_var = "KEYLESS_API_KEY"
    api_key_required = False

    def _model_name(self, model_id: str) -> str:
        return "keyless-model"

    def model_name_for_test(self, model_id: str) -> str:
        return self._model_name(model_id)

    def provider_model_name_for_test(self, model_id: str) -> str:
        return self._provider_model_name(model_id)


def test_requires_api_key_error_message_is_provider_specific() -> None:
    """Test that missing API key errors mention the correct provider name/env var."""
    original = os.environ.pop("DUMMY_API_KEY", None)
    try:
        with pytest.raises(ValueError) as exc_info:
            _DummyProvider()
        message = str(exc_info.value)
        assert "Dummy API key is required" in message
        assert "DUMMY_API_KEY" in message
    finally:
        if original is not None:
            os.environ["DUMMY_API_KEY"] = original


def test_default_base_url_with_no_key_uses_dummy_key_for_sdk_init() -> None:
    """Test that providers with default_base_url can initialize without api_key."""
    original = os.environ.pop("KEYLESS_API_KEY", None)
    try:
        with (
            patch(
                "mirascope.llm.providers.openai.completions.base_provider.OpenAI"
            ) as openai_client,
            patch(
                "mirascope.llm.providers.openai.completions.base_provider.AsyncOpenAI"
            ) as async_openai_client,
        ):
            openai_client.return_value = MagicMock()
            async_openai_client.return_value = MagicMock()

            _KeylessProvider()

            openai_client.assert_called_once()
            async_openai_client.assert_called_once()

            assert openai_client.call_args.kwargs["api_key"] == "not-needed"
            assert openai_client.call_args.kwargs["base_url"] == "https://example.com"

            assert async_openai_client.call_args.kwargs["api_key"] == "not-needed"
            assert (
                async_openai_client.call_args.kwargs["base_url"]
                == "https://example.com"
            )
    finally:
        if original is not None:
            os.environ["KEYLESS_API_KEY"] = original


def test_default_provider_model_name_matches_model_name() -> None:
    """Test that default _provider_model_name delegates to _model_name."""
    with (
        patch(
            "mirascope.llm.providers.openai.completions.base_provider.OpenAI"
        ) as openai_client,
        patch(
            "mirascope.llm.providers.openai.completions.base_provider.AsyncOpenAI"
        ) as async_openai_client,
    ):
        openai_client.return_value = MagicMock()
        async_openai_client.return_value = MagicMock()

        provider = _KeylessProvider()
        assert provider.provider_model_name_for_test(
            "anything"
        ) == provider.model_name_for_test("anything")
