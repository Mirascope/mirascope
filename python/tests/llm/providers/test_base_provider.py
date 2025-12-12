"""Tests for the base Provider class and context management."""

from typing import Any
from unittest.mock import Mock

import pytest

from mirascope import llm


class MockProvider(llm.Provider[Any]):
    """Mock provider for testing."""

    provider_id = "mock"
    default_scope = "mock/"


class AnotherMockProvider(llm.Provider[Any]):
    """Another mock provider for testing different scopes."""

    provider_id = "another"
    default_scope = "another/"


def test_provider_initialization() -> None:
    """Test that Provider can be initialized with a client."""
    mock_client = Mock()
    provider = MockProvider(client=mock_client)

    assert provider.client is mock_client
    assert provider.provider_id == "mock"
    assert provider.default_scope == "mock/"


def test_provider_context_manager_basic() -> None:
    """Test that Provider works as a context manager."""
    mock_client = Mock()
    provider = MockProvider(client=mock_client)

    # Before entering context, no provider should be found
    assert llm.provider_for_model("mock/model-1") is None

    # Inside context, provider should be available
    with provider:
        assert llm.provider_for_model("mock/model-1") is provider
        assert llm.provider_for_model("mock/another-model") is provider

    # After exiting context, provider should no longer be available
    assert llm.provider_for_model("mock/model-1") is None


def test_provider_scope_matching() -> None:
    """Test that providers only match models within their scope."""
    mock_client = Mock()
    provider = MockProvider(client=mock_client)

    with provider:
        # Should match models with "mock/" prefix
        assert llm.provider_for_model("mock/model-1") is provider
        assert llm.provider_for_model("mock/other") is provider

        # Should NOT match models with different prefix
        assert llm.provider_for_model("anthropic/claude") is None
        assert llm.provider_for_model("openai/gpt-4") is None
        assert llm.provider_for_model("other/model") is None


def test_nested_providers_same_instance() -> None:
    """Test that the same provider instance can be nested."""
    mock_client = Mock()
    provider = MockProvider(client=mock_client)

    # Not available outside any context
    assert llm.provider_for_model("mock/model") is None

    with provider:
        # Available in outer context
        assert llm.provider_for_model("mock/model") is provider

        with provider:
            # Still available in nested context
            assert llm.provider_for_model("mock/model") is provider

        # Still available after inner context exits
        assert llm.provider_for_model("mock/model") is provider

    # Not available after all contexts exit
    assert llm.provider_for_model("mock/model") is None


def test_nested_providers_different_scopes() -> None:
    """Test multiple providers with different scopes in nested contexts."""
    mock_client1 = Mock()
    mock_client2 = Mock()
    provider1 = MockProvider(client=mock_client1)
    provider2 = AnotherMockProvider(client=mock_client2)

    with provider1:
        # Only provider1 in scope
        assert llm.provider_for_model("mock/model") is provider1
        assert llm.provider_for_model("another/model") is None

        with provider2:
            # Both providers in scope
            assert llm.provider_for_model("mock/model") is provider1
            assert llm.provider_for_model("another/model") is provider2

        # Back to just provider1
        assert llm.provider_for_model("mock/model") is provider1
        assert llm.provider_for_model("another/model") is None

    # All contexts exited
    assert llm.provider_for_model("mock/model") is None
    assert llm.provider_for_model("another/model") is None


def test_multiple_contexts_parallel() -> None:
    """Test using multiple providers in parallel (not nested)."""
    mock_client1 = Mock()
    mock_client2 = Mock()
    provider1 = MockProvider(client=mock_client1)
    provider2 = AnotherMockProvider(client=mock_client2)

    # Use context manager syntax that creates multiple contexts at once
    with provider1, provider2:
        # Each provider matches its scope
        assert llm.provider_for_model("mock/model") is provider1
        assert llm.provider_for_model("another/model") is provider2

    # After exiting, neither provider is available
    assert llm.provider_for_model("mock/model") is None
    assert llm.provider_for_model("another/model") is None


def test_last_wins_semantics() -> None:
    """Test that later contexts override earlier ones for the same scope."""

    class OverrideMockProvider(llm.Provider[Any]):
        """Another provider with the same scope as MockProvider."""

        provider_id = "override"
        default_scope = "mock/"  # Same scope as MockProvider

    mock_client1 = Mock()
    mock_client2 = Mock()
    provider1 = MockProvider(client=mock_client1)
    provider2 = OverrideMockProvider(client=mock_client2)

    with provider1:
        assert llm.provider_for_model("mock/model") is provider1

        with provider2:
            # provider2 comes later, should win for "mock/" scope
            assert llm.provider_for_model("mock/model") is provider2

        # Back to provider1
        assert llm.provider_for_model("mock/model") is provider1


def test_provider_for_model_empty_context() -> None:
    """Test llm.provider_for_model when no providers are in context."""
    assert llm.provider_for_model("mock/model") is None
    assert llm.provider_for_model("anthropic/claude") is None
    assert llm.provider_for_model("any/model") is None


def test_provider_context_isolation() -> None:
    """Test that provider contexts don't leak between uses."""
    # This test verifies cleanup works properly
    mock_client = Mock()
    provider = MockProvider(client=mock_client)

    # Start with no provider available
    assert llm.provider_for_model("mock/model") is None

    with provider:
        assert llm.provider_for_model("mock/model") is provider

    # Should be clean after exiting
    assert llm.provider_for_model("mock/model") is None

    # Try again to ensure no state leaked
    with provider:
        assert llm.provider_for_model("mock/model") is provider

    assert llm.provider_for_model("mock/model") is None


def test_provider_exception_handling() -> None:
    """Test that provider context is cleaned up even if exception occurs."""
    mock_client = Mock()
    provider = MockProvider(client=mock_client)

    # No provider before entering context
    assert llm.provider_for_model("mock/model") is None

    with pytest.raises(ValueError, match="test error"), provider:
        # Provider is available inside context
        assert llm.provider_for_model("mock/model") is provider
        raise ValueError("test error")

    # Context should still be cleaned up after exception
    assert llm.provider_for_model("mock/model") is None


def test_provider_returns_self_from_enter() -> None:
    """Test that __enter__ returns the provider instance."""
    mock_client = Mock()
    provider = MockProvider(client=mock_client)

    with provider as p:
        assert p is provider
        assert p.client is mock_client
