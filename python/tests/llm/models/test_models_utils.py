"""Tests for the LLM models _utils module."""

from unittest.mock import Mock, patch

import pytest

from mirascope import llm


@pytest.fixture
def anthropic_client() -> Mock:
    """Create a mock Anthropic client."""
    return Mock(spec=llm.AnthropicClient)


@pytest.fixture
def google_client() -> Mock:
    """Create a mock Google client."""
    return Mock(spec=llm.GoogleClient)


@pytest.fixture
def openai_client() -> Mock:
    """Create a mock OpenAI client."""
    return Mock(spec=llm.OpenAIClient)


@pytest.fixture
def params() -> llm.clients.BaseParams:
    return llm.clients.BaseParams({"temperature": 0.7, "max_tokens": 100})


@patch.object(llm.LLM, "create")
def test_assumed_safe_llm_create_anthropic_with_client(
    mock_create: Mock, anthropic_client: Mock, params: llm.clients.BaseParams
) -> None:
    """Test assumed_safe_llm_create for Anthropic with custom client."""
    mock_llm = Mock(spec=llm.LLM)
    mock_create.return_value = mock_llm

    result = llm.models._utils.assumed_safe_llm_create(
        provider="anthropic",
        model="claude-3-5-sonnet-20241022",
        client=anthropic_client,
        params=params,
    )

    mock_create.assert_called_once_with(
        provider="anthropic",
        client=anthropic_client,
        model="claude-3-5-sonnet-20241022",
        params=params,
    )
    assert result is mock_llm


@patch.object(llm.LLM, "create")
def test_assumed_safe_llm_create_anthropic_without_client(
    mock_create: Mock, params: llm.clients.BaseParams
) -> None:
    """Test assumed_safe_llm_create for Anthropic without custom client."""
    mock_llm = Mock(spec=llm.LLM)
    mock_create.return_value = mock_llm

    result = llm.models._utils.assumed_safe_llm_create(
        provider="anthropic",
        model="claude-3-5-haiku-20241022",
        client=None,
        params=params,
    )

    mock_create.assert_called_once_with(
        provider="anthropic",
        client=None,
        model="claude-3-5-haiku-20241022",
        params=params,
    )
    assert result is mock_llm


@patch.object(llm.LLM, "create")
def test_assumed_safe_llm_create_google_with_client(
    mock_create: Mock, google_client: Mock, params: llm.clients.BaseParams
) -> None:
    """Test assumed_safe_llm_create for Google with custom client."""
    mock_llm = Mock(spec=llm.LLM)
    mock_create.return_value = mock_llm

    result = llm.models._utils.assumed_safe_llm_create(
        provider="google", model="gemini-1.5-flash", client=google_client, params=params
    )

    mock_create.assert_called_once_with(
        provider="google", client=google_client, model="gemini-1.5-flash", params=params
    )
    assert result is mock_llm


@patch.object(llm.LLM, "create")
def test_assumed_safe_llm_create_google_without_client(
    mock_create: Mock, params: llm.clients.BaseParams
) -> None:
    """Test assumed_safe_llm_create for Google without custom client."""
    mock_llm = Mock(spec=llm.LLM)
    mock_create.return_value = mock_llm

    result = llm.models._utils.assumed_safe_llm_create(
        provider="google", model="gemini-1.5-pro", client=None, params=params
    )

    mock_create.assert_called_once_with(
        provider="google", client=None, model="gemini-1.5-pro", params=params
    )
    assert result is mock_llm


@patch.object(llm.LLM, "create")
def test_assumed_safe_llm_create_openai_with_client(
    mock_create: Mock, openai_client: Mock, params: llm.clients.BaseParams
) -> None:
    """Test assumed_safe_llm_create for OpenAI with custom client."""
    mock_llm = Mock(spec=llm.LLM)
    mock_create.return_value = mock_llm

    result = llm.models._utils.assumed_safe_llm_create(
        provider="openai", model="gpt-4o-mini", client=openai_client, params=params
    )

    mock_create.assert_called_once_with(
        provider="openai", client=openai_client, model="gpt-4o-mini", params=params
    )
    assert result is mock_llm


@patch.object(llm.LLM, "create")
def test_assumed_safe_llm_create_openai_without_client(
    mock_create: Mock, params: llm.clients.BaseParams
) -> None:
    """Test assumed_safe_llm_create for OpenAI without custom client."""
    mock_llm = Mock(spec=llm.LLM)
    mock_create.return_value = mock_llm

    result = llm.models._utils.assumed_safe_llm_create(
        provider="openai", model="gpt-4o", client=None, params=params
    )

    mock_create.assert_called_once_with(
        provider="openai", client=None, model="gpt-4o", params=params
    )
    assert result is mock_llm


def test_assumed_safe_llm_create_unknown_provider() -> None:
    """Test that unknown provider raises ValueError."""
    with pytest.raises(ValueError, match="Unknown provider: unknown"):
        llm.models._utils.assumed_safe_llm_create(
            provider="unknown",  # type: ignore[arg-type]
            model="some-model",
            client=None,
            params={},
        )


@patch.object(llm.LLM, "create")
def test_assumed_safe_llm_create_empty_params(mock_create: Mock) -> None:
    """Test assumed_safe_llm_create with empty params."""
    mock_llm = Mock(spec=llm.LLM)
    mock_create.return_value = mock_llm

    result = llm.models._utils.assumed_safe_llm_create(
        provider="openai", model="gpt-4o-mini", client=None, params={}
    )

    mock_create.assert_called_once_with(
        provider="openai", client=None, model="gpt-4o-mini", params={}
    )
    assert result is mock_llm
