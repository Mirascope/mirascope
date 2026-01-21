"""Tests for provider registry functionality."""

import os
from collections.abc import Generator
from contextlib import contextmanager

import pytest

from mirascope import llm
from mirascope.llm.providers.provider_registry import (
    DEFAULT_AUTO_REGISTER_SCOPES,
)


@contextmanager
def env_without(*keys: str) -> Generator[None, None, None]:
    """Temporarily remove environment variables for testing."""
    original_values = {key: os.environ.pop(key, None) for key in keys}
    try:
        yield
    finally:
        for key, value in original_values.items():
            if value is not None:
                os.environ[key] = value


def test_auto_registered_providers() -> None:
    """Test that providers auto-register on first use and are cached."""
    openai = llm.providers.get_provider_for_model("openai/gpt-5")
    assert openai is llm.providers.get_provider_for_model("openai/gpt-4")


def test_provider_registration() -> None:
    """Test explicit provider registration."""
    custom_openai = llm.register_provider("openai", api_key="foo-bar")
    assert llm.providers.get_provider_for_model("openai/gpt-5") is custom_openai


def test_provider_registry_reset() -> None:
    """Test resetting the provider registry."""
    custom_openai = llm.register_provider("openai", api_key="foo-bar")
    llm.reset_provider_registry()
    assert llm.providers.get_provider_for_model("openai/gpt-5") is not custom_openai


def test_provider_as_argument() -> None:
    """Test that you can pass a Provider to register_provider"""
    custom_openai = llm.providers.OpenAIProvider()
    as_registered = llm.register_provider(custom_openai)
    assert custom_openai is as_registered
    assert llm.providers.get_provider_for_model("openai/gpt-5") is custom_openai


def test_longest_scope_wins() -> None:
    """Test that the longest matching scope takes precedence."""
    default_openai = llm.register_provider("openai")
    custom_openai = llm.register_provider(
        "openai", scope="openai/gpt-5", api_key="foo-bar"
    )
    assert default_openai is not custom_openai
    assert llm.providers.get_provider_for_model("openai/gpt-4") is default_openai
    assert llm.providers.get_provider_for_model("openai/gpt-5") is custom_openai


def test_register_provider_with_multiple_scopes() -> None:
    """Test registering a provider for multiple scopes (e.g., AWS Bedrock)."""
    provider = llm.register_provider("anthropic", scope=["anthropic/", "aws/"])
    assert llm.providers.get_provider_for_model("anthropic/claude") is provider
    assert llm.providers.get_provider_for_model("aws/claude") is provider


def test_all_default_scopes_auto_register() -> None:
    """Test that all built-in providers can auto-register dynamically."""
    for scope, fallback_chain in DEFAULT_AUTO_REGISTER_SCOPES.items():
        # Get the primary (first) provider in the fallback chain
        primary_provider_id = fallback_chain[0].provider_id

        # Skip mlx as it won't run in CI
        if primary_provider_id == "mlx":
            continue

        # Test with a fake model under this scope
        model_id = f"{scope}test-model"
        provider = llm.providers.get_provider_for_model(model_id)
        assert provider.id == primary_provider_id


def test_explicit_registration_overrides_auto() -> None:
    """Test that explicit registration takes precedence over auto-registration."""
    # Register a different provider for openai scope
    custom = llm.register_provider("anthropic", scope="openai/")

    # Should use explicit registration, not auto-registration
    assert llm.providers.get_provider_for_model("openai/gpt-4") is custom
    assert custom.id == "anthropic"


def test_no_provider_raises_error() -> None:
    """Test that unknown provider prefixes raise NoRegisteredProviderError."""
    with pytest.raises(llm.NoRegisteredProviderError) as exc_info:
        llm.providers.get_provider_for_model("unknown/model")

    assert exc_info.value.model_id == "unknown/model"
    assert "No provider registered" in str(exc_info.value)


def test_most_specific_scope_wins() -> None:
    """Test that more specific scopes win over less specific ones."""
    p1 = llm.register_provider("openai", scope="openai/")
    p2 = llm.register_provider("anthropic", scope="openai/gpt-4")
    p3 = llm.register_provider("google", scope="openai/gpt-4-turbo")

    assert llm.providers.get_provider_for_model("openai/gpt-3") is p1
    assert llm.providers.get_provider_for_model("openai/gpt-4o") is p2
    assert llm.providers.get_provider_for_model("openai/gpt-4-turbo-2024") is p3


def test_empty_string_scope_matches_everything() -> None:
    """Test that empty string scope acts as a catch-all."""
    catch_all = llm.register_provider("openai", scope="")

    # Should match any model since "" is a prefix of everything
    assert llm.providers.get_provider_for_model("anything/model") is catch_all
    assert llm.providers.get_provider_for_model("foo/bar") is catch_all


def test_empty_string_scope_loses_to_specific() -> None:
    """Test that empty string scope has lowest precedence."""
    catch_all = llm.register_provider("openai", scope="")
    specific = llm.register_provider("anthropic", scope="anthropic/")

    # Specific scope should win
    assert llm.providers.get_provider_for_model("anthropic/claude") is specific
    # But catch-all should still work for unknown scopes
    assert llm.providers.get_provider_for_model("random/model") is catch_all


def test_empty_array_scope_registers_nothing() -> None:
    """Test that registering with empty scope list doesn't register any scopes."""
    custom_openai = llm.register_provider("openai", api_key="1234", scope=[])

    actual = llm.providers.get_provider_for_model("openai/gpt-5")
    # Will use the default provider (via auto registration) since no scope was provided
    # for the custom provider
    assert actual is not custom_openai


def test_overwrite_provider_registration() -> None:
    """Test that registering a provider for the same scope overwrites the previous one."""
    # Register first provider
    provider1 = llm.register_provider("openai", scope="custom/", api_key="key1")
    assert llm.providers.get_provider_for_model("custom/model") is provider1

    # Register second provider for the same scope - should overwrite
    provider2 = llm.register_provider("anthropic", scope="custom/")
    assert llm.providers.get_provider_for_model("custom/model") is provider2
    assert provider2 is not provider1

    # Verify the first provider is no longer used
    result = llm.providers.get_provider_for_model("custom/model")
    assert result.id == "anthropic"
    assert result is not provider1


# =============================================================================
# Mirascope Fallback Tests
# =============================================================================


def test_direct_provider_preferred_when_key_available() -> None:
    """Test that direct provider is used when its API key is available."""
    # Both ANTHROPIC_API_KEY and MIRASCOPE_API_KEY are set (via conftest)
    llm.reset_provider_registry()
    provider = llm.providers.get_provider_for_model("anthropic/claude-4-5-sonnet")

    # Should use the direct Anthropic provider, not Mirascope
    assert provider.id == "anthropic"
    assert isinstance(provider, llm.providers.AnthropicProvider)


def test_mirascope_fallback_when_direct_key_missing() -> None:
    """Test fallback to Mirascope when direct provider key is missing."""
    llm.reset_provider_registry()

    with env_without("ANTHROPIC_API_KEY"):
        provider = llm.providers.get_provider_for_model("anthropic/claude-4-5-sonnet")

        # Should fall back to Mirascope provider
        assert provider.id == "mirascope"
        assert isinstance(provider, llm.providers.MirascopeProvider)


def test_mirascope_fallback_registers_only_for_invoked_scope() -> None:
    """Test that Mirascope fallback only registers for the specific scope used."""
    llm.reset_provider_registry()

    with env_without("GOOGLE_API_KEY"):
        # Request a Google model - should fall back to Mirascope for google/ scope
        google_provider = llm.providers.get_provider_for_model("google/gemini-2.5-pro")
        assert google_provider.id == "mirascope"

        # Now request an Anthropic model - should use direct Anthropic
        # (ANTHROPIC_API_KEY is still set)
        anthropic_provider = llm.providers.get_provider_for_model(
            "anthropic/claude-4-5-sonnet"
        )
        assert anthropic_provider.id == "anthropic"

        # Verify Mirascope was NOT registered for anthropic/ scope
        # (it was only registered for google/)
        assert google_provider is not anthropic_provider


def test_missing_api_key_error_with_mirascope_fallback_suggestion() -> None:
    """Test error message suggests Mirascope when it's a valid fallback."""
    llm.reset_provider_registry()

    with env_without("ANTHROPIC_API_KEY", "MIRASCOPE_API_KEY"):
        with pytest.raises(llm.MissingAPIKeyError) as exc_info:
            llm.providers.get_provider_for_model("anthropic/claude-4-5-sonnet")

        error = exc_info.value
        assert error.provider_id == "anthropic"
        assert error.env_var == "ANTHROPIC_API_KEY"

        # Error message should mention both options
        message = str(error)
        assert "ANTHROPIC_API_KEY" in message
        assert "MIRASCOPE_API_KEY" in message
        assert "Mirascope Router" in message


def test_missing_api_key_error_without_mirascope_suggestion() -> None:
    """Test error message doesn't suggest Mirascope for unsupported scopes."""
    llm.reset_provider_registry()

    with env_without("TOGETHER_API_KEY"):
        with pytest.raises(llm.MissingAPIKeyError) as exc_info:
            llm.providers.get_provider_for_model("together/meta-llama/Llama-3.3-70B")

        error = exc_info.value
        assert error.provider_id == "together"
        assert error.env_var == "TOGETHER_API_KEY"

        # Error message should NOT mention Mirascope (not a valid fallback)
        message = str(error)
        assert "TOGETHER_API_KEY" in message
        assert "MIRASCOPE_API_KEY" not in message
        assert "Mirascope Router" not in message


def test_providers_without_api_key_requirement() -> None:
    """Test that providers like Ollama work without any API keys."""
    llm.reset_provider_registry()

    # Remove all API keys - Ollama should still work
    with env_without(
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "MIRASCOPE_API_KEY",
        "OPENAI_API_KEY",
        "TOGETHER_API_KEY",
        "OLLAMA_API_KEY",
    ):
        provider = llm.providers.get_provider_for_model("ollama/llama3.2")

        # Should successfully return OllamaProvider
        assert provider.id == "ollama"
        assert isinstance(provider, llm.providers.OllamaProvider)
