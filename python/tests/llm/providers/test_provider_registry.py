"""Tests for provider registry functionality."""

from collections.abc import Generator

import pytest

from mirascope import llm
from mirascope.llm.providers.provider_registry import (
    DEFAULT_AUTO_REGISTER_SCOPES,
    PROVIDER_REGISTRY,
)


@pytest.fixture(autouse=True)
def reset_provider_registry() -> Generator[None, None, None]:
    """Reset the provider registry before and after each test."""
    PROVIDER_REGISTRY.clear()
    yield
    PROVIDER_REGISTRY.clear()


def test_auto_registered_providers() -> None:
    """Test that providers auto-register on first use and are cached."""
    openai = llm.providers.get_provider_for_model("openai/gpt-5")
    assert openai is llm.load_provider("openai")
    assert openai is llm.providers.get_provider_for_model("openai/gpt-4")


def test_provider_registration() -> None:
    """Test explicit provider registration."""
    custom_openai = llm.register_provider("openai", api_key="foo-bar")
    assert llm.providers.get_provider_for_model("openai/gpt-5") is custom_openai


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
    for scope, provider_id in DEFAULT_AUTO_REGISTER_SCOPES.items():
        # Skip mlx as it won't run in CI
        if provider_id == "mlx":
            continue

        # Test with a fake model under this scope
        model_id = f"{scope}test-model"
        provider = llm.providers.get_provider_for_model(model_id)
        assert provider.id == provider_id


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
    custom_openai = llm.load_provider("openai", api_key="1234")
    llm.register_provider(custom_openai, scope=[])

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
