"""Tests for the Model class."""

from collections.abc import Generator

import pytest

from mirascope import llm
from mirascope.llm.providers.provider_registry import PROVIDER_REGISTRY


@pytest.fixture(autouse=True)
def reset_provider_registry() -> Generator[None, None, None]:
    """Reset the provider registry before and after each test."""
    PROVIDER_REGISTRY.clear()
    yield
    PROVIDER_REGISTRY.clear()


def test_use_model_without_context() -> None:
    """Test that use_model creates a new Model when no context is set."""
    model = llm.use_model("openai/gpt-4o")

    assert model.provider_id == "openai"
    assert model.model_id == "openai/gpt-4o"


def test_use_model_with_context() -> None:
    """Test that use_model returns the context model when one is set."""
    with llm.model("anthropic/claude-sonnet-4-0"):
        model = llm.use_model("openai/gpt-4o")

        assert model.provider_id == "anthropic"
        assert model.model_id == "anthropic/claude-sonnet-4-0"


def test_use_model_as_context_manager() -> None:
    """Test that model can be used as a context manager directly."""
    with llm.Model("anthropic/claude-sonnet-4-0"):
        model = llm.use_model("openai/gpt-4o")

        assert model.provider_id == "anthropic"
        assert model.model_id == "anthropic/claude-sonnet-4-0"


def test_direct_model_instantiation_ignores_context() -> None:
    """Test that direct Model instantiation ignores context (hardcoding behavior)."""
    with llm.model("openai/claude-sonnet-4-0"):
        model = llm.Model("openai/gpt-4o")

        assert model.provider_id == "openai"
        assert model.model_id == "openai/gpt-4o"


def test_value_error_invalid_models() -> None:
    """Test that invalid model_ids raise appropriate errors."""

    # Test unregistered provider - need to actually call to trigger runtime error
    @llm.call("nonexistent/gpt-5-mini")
    def say_hi() -> str:
        return "hi"

    with pytest.raises(llm.NoRegisteredProviderError, match="No provider registered"):
        say_hi()

    # Test invalid model_id format (no slash)
    with pytest.raises(ValueError, match="Invalid model_id format"):
        llm.call("really-cool-model-i-heard-about")


def test_use_model_accepts_model_instance() -> None:
    """Test that use_model accepts a Model instance."""
    model_instance = llm.Model("anthropic/claude-sonnet-4-0", temperature=0.7)
    model = llm.use_model(model_instance)

    assert model.provider_id == "anthropic"
    assert model.model_id == "anthropic/claude-sonnet-4-0"
    assert model.params.get("temperature") == 0.7


def test_nested_context_manager_with_same_instance() -> None:
    """Test that the same Model instance can be used in nested contexts.

    Expected behavior: Each nested context should properly manage its own token
    and restore the previous state when exiting.
    """
    model = llm.Model("openai/gpt-4o")

    assert llm.model_from_context() is None

    with model:
        assert llm.model_from_context() is model

        with model:  # Inner context with SAME instance
            assert llm.model_from_context() is model

        assert llm.model_from_context() is model, (
            "Context should still be active after nested exit, but token was lost"
        )

    assert llm.model_from_context() is None


def test_provider_resolution_is_dynamic() -> None:
    """Test that Model dynamically resolves provider based on registry changes.

    This ensures that changes to the provider registry affect which provider
    is used by Model instances, even after the Model is created.
    """
    # Create a model - should auto-register and use default OpenAI provider
    model = llm.Model("openai/gpt-4o")
    initial_provider = model.provider
    assert initial_provider.id == "openai"

    # Register a custom provider for the same scope
    custom_provider = llm.register_provider("anthropic", scope="openai/")

    # The same Model instance should now resolve to the custom provider
    assert model.provider is custom_provider
    assert model.provider.id == "anthropic"

    # Register another provider for a more specific scope
    very_specific_provider = llm.register_provider("google", scope="openai/gpt-4o")

    # Should now use the most specific provider
    assert model.provider is very_specific_provider
    assert model.provider.id == "google"

    # A different model should use less specific provider
    other_model = llm.Model("openai/gpt-3.5-turbo")
    assert other_model.provider is custom_provider
    assert other_model.provider.id == "anthropic"
