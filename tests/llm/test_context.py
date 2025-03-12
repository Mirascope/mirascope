"""Tests for the _context.py module."""

from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from mirascope.core.base import BaseTool, CommonCallParams
from mirascope.llm._context import (
    CallArgs,
    LLMContext,
    _context,
    apply_context_overrides_to_call_args,
    context,
    get_current_context,
)


class MockTool(BaseTool):
    """Mock tool for testing."""

    name: str = "mock_tool"
    description: str = "Mock tool for testing"


class MockResponseModel(BaseModel):
    """Mock response model for testing."""

    value: str


def test_basic_context_enter_exit():
    """Test basic enter and exit functionality of LLMContext."""
    # Test enter
    ctx = LLMContext(provider="openai", model="gpt-4")
    with ctx as entered_ctx:
        assert entered_ctx is ctx
        assert get_current_context() is ctx

    # Test exit - context should be cleared
    assert get_current_context() is None


def test_context_no_old_context():
    """Test creating a context when there's no old context."""
    with _context(
        provider="openai",
        model="gpt-4",
        stream=True,
        tools=[MockTool],
        response_model=MockResponseModel,
        output_parser=lambda x: x,
        json_mode=True,
        client=MagicMock(),
        call_params=CommonCallParams(),
    ) as ctx:
        assert ctx.provider == "openai"
        assert ctx.model == "gpt-4"
        assert ctx.stream is True
        assert ctx.tools == [MockTool]
        assert ctx.response_model == MockResponseModel
        assert ctx.output_parser is not None
        assert ctx.json_mode is True
        assert ctx.client is not None
        assert ctx.call_params is not None


def test_context_with_old_context():
    """Test creating a nested context with an existing context."""
    with (
        _context(
            provider="openai",
            model="gpt-3.5-turbo",
            stream=False,
            tools=None,
            response_model=None,
            output_parser=None,
            json_mode=False,
            client=None,
            call_params=None,
        ),
        _context(
            provider="anthropic",
            model="claude-3-opus",
            stream=True,
            tools=None,
            response_model=None,
            output_parser=None,
            json_mode=None,
            client=None,
            call_params=None,
        ) as ctx2,
    ):
        # Now create a new context inside the first one
        # The new context should override fields that were set
        assert ctx2.provider == "anthropic"
        assert ctx2.model == "claude-3-opus"
        assert ctx2.stream is True

        # Other fields should have remained None since they were not set in either context
        assert ctx2.tools is None
        assert ctx2.response_model is None


def test_nested_context_with_partial_override():
    """Test creating a nested context with only some fields overridden."""
    mock_client1 = MagicMock()
    mock_client2 = MagicMock()
    call_params1 = CommonCallParams()

    with (
        _context(
            provider="openai",
            model="gpt-4o",
            stream=False,
            tools=[MockTool],
            response_model=MockResponseModel,
            output_parser=lambda x: x,
            json_mode=True,
            client=mock_client1,
            call_params=call_params1,
        ) as ctx1,
        _context(
            provider="openai",  # same provider
            model="gpt-4o-mini",  # different model
            stream=None,  # not overridden
            tools=None,  # not overridden
            response_model=None,  # not overridden
            output_parser=None,  # not overridden
            json_mode=None,  # not overridden
            client=mock_client2,  # different client
            call_params=None,  # not overridden
        ) as ctx2,
    ):
        # Check overridden fields
        assert ctx2.provider == "openai"
        assert ctx2.model == "gpt-4o-mini"
        assert ctx2.client is mock_client2

        # Check inherited fields
        assert ctx2.stream is ctx1.stream
        assert ctx2.tools is ctx1.tools
        assert ctx2.response_model is ctx1.response_model
        assert ctx2.output_parser is ctx1.output_parser
        assert ctx2.json_mode is ctx1.json_mode
        assert ctx2.call_params is ctx1.call_params


def test_apply_context_overrides_to_call_args_no_context():
    """Test applying context overrides when no context is active."""
    call_args: CallArgs = {
        "provider": "openai",
        "model": "gpt-4",
        "stream": False,
        "tools": None,
        "response_model": None,
        "output_parser": None,
        "json_mode": False,
        "client": None,
        "call_params": None,
    }

    # With no active context, call_args should be returned unchanged
    with patch("mirascope.llm._context.get_current_context", return_value=None):
        result = apply_context_overrides_to_call_args(call_args)
        assert result == call_args


def test_apply_context_overrides_to_call_args_structural_overrides():
    """Test applying context with structural overrides."""
    # Original call args
    call_args: CallArgs = {
        "provider": "openai",
        "model": "gpt-4",
        "stream": False,
        "tools": [MockTool],
        "response_model": None,
        "output_parser": None,
        "json_mode": False,
        "client": None,
        "call_params": None,
    }

    # Create a context with structural overrides
    with patch("mirascope.llm._context.get_current_context") as mock_get_context:
        # Mock a context with stream override (structural)
        mock_get_context.return_value = LLMContext(
            provider="anthropic",
            model="claude-3",
            stream=True,  # structural override
            response_model=MockResponseModel,  # structural override
            output_parser=lambda x: x,  # structural override
        )

        result = apply_context_overrides_to_call_args(call_args)

        # Check that overrides were applied
        assert result["provider"] == "anthropic"
        assert result["model"] == "claude-3"
        assert result["stream"] is True
        assert result["response_model"] == MockResponseModel
        assert result["output_parser"] is not None

        # Check that we reset other structural fields
        assert result["tools"] is None


def test_apply_context_overrides_to_call_args_response_model_override():
    """Test applying context with response_model override specifically."""
    # Original call args
    call_args: CallArgs = {
        "provider": "openai",
        "model": "gpt-4",
        "stream": False,
        "tools": [MockTool],
        "response_model": None,
        "output_parser": None,
        "json_mode": False,
        "client": None,
        "call_params": None,
    }

    # Create a context with response_model override
    with patch("mirascope.llm._context.get_current_context") as mock_get_context:
        # Mock a context with response_model override (forces tools to None)
        mock_get_context.return_value = LLMContext(
            provider="openai",
            model="gpt-4",
            response_model=MockResponseModel,  # This should reset tools
        )

        result = apply_context_overrides_to_call_args(call_args)

        # Check that response_model override forces tools to None
        assert result["response_model"] == MockResponseModel
        assert result["tools"] is None


def test_apply_context_overrides_to_call_args_all_possible_overrides():
    """Test applying context with all possible overrides."""
    # Original call args
    call_args: CallArgs = {
        "provider": "openai",
        "model": "gpt-4",
        "stream": False,
        "tools": None,
        "response_model": None,
        "output_parser": None,
        "json_mode": False,
        "client": None,
        "call_params": None,
    }

    # Create a mock for client and call params
    mock_client = MagicMock()
    call_params = CommonCallParams(temperature=0.8)

    # Create a context with all possible overrides
    with patch("mirascope.llm._context.get_current_context") as mock_get_context:
        # Mock a context with all fields overridden
        mock_context = LLMContext(
            provider="anthropic",
            model="claude-3",
            stream=True,
            tools=[MockTool],
            response_model=MockResponseModel,
            output_parser=lambda x: x,
            json_mode=True,
            client=mock_client,
            call_params=call_params,
        )
        mock_get_context.return_value = mock_context

        result = apply_context_overrides_to_call_args(call_args)

        # Check that all overrides were applied
        assert result["provider"] == "anthropic"
        assert result["model"] == "claude-3"
        assert result["stream"] is True
        assert result["tools"] is mock_context.tools
        assert result["response_model"] is mock_context.response_model
        assert result["output_parser"] is mock_context.output_parser
        assert result["json_mode"] is mock_context.json_mode
        assert result["client"] is mock_context.client
        assert result["call_params"] is mock_context.call_params


def test_context_function_validation():
    """Test the context function validation."""
    # Test that it raises error if only provider is provided
    with pytest.raises(ValueError):
        context(provider="openai", model=None)  # pyright: ignore [reportCallIssue,reportArgumentType]

    # Test that it raises error if only model is provided
    with pytest.raises(ValueError):
        context(provider=None, model="gpt-4")  # pyright: ignore [reportCallIssue,reportArgumentType]


def test_context_function():
    """Test the public context function."""
    with patch("mirascope.llm._context._context") as mock_context:
        mock_context.return_value = LLMContext(provider="openai", model="gpt-4")

        with context(provider="openai", model="gpt-4"):
            pass

        # Verify that _context was called with the right parameters
        mock_context.assert_called_once_with(
            provider="openai", model="gpt-4", client=None, call_params=None
        )


def test_context_function_with_client_and_params():
    """Test the public context function with client and call parameters."""
    mock_client = MagicMock()
    call_params = CommonCallParams(temperature=0.5)

    with patch("mirascope.llm._context._context") as mock_context:
        mock_context.return_value = LLMContext(
            provider="openai",
            model="gpt-4",
            client=mock_client,
            call_params=call_params,
        )

        with context(
            provider="openai",
            model="gpt-4",
            client=mock_client,
            call_params=call_params,
        ):
            pass

        # Verify that _context was called with the right parameters
        mock_context.assert_called_once_with(
            provider="openai",
            model="gpt-4",
            client=mock_client,
            call_params=call_params,
        )


def test_apply_context_overrides_to_call_args_with_explicit_context():
    """Test applying context overrides with an explicitly provided context."""
    # Original call args
    call_args: CallArgs = {
        "provider": "openai",
        "model": "gpt-4",
        "stream": False,
        "tools": None,
        "response_model": None,
        "output_parser": None,
        "json_mode": False,
        "client": None,
        "call_params": None,
    }

    # Create an explicit context
    explicit_context = LLMContext(
        provider="anthropic",
        model="claude-3-5-sonnet",
        stream=True,
    )

    # Apply the explicit context
    result = apply_context_overrides_to_call_args(
        call_args, context_override=explicit_context
    )

    # Check that the explicit context was applied
    assert result["provider"] == "anthropic"
    assert result["model"] == "claude-3-5-sonnet"
    assert result["stream"] is True

    # Test that it takes precedence over the current context
    with _context(
        provider="openai",
        model="gpt-4o",
        stream=False,
    ):
        # The explicit context should be used, not the current context
        result = apply_context_overrides_to_call_args(
            call_args, context_override=explicit_context
        )
        assert result["provider"] == "anthropic"
        assert result["model"] == "claude-3-5-sonnet"
        assert result["stream"] is True
