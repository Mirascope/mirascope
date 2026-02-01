"""Tests for Anthropic provider instrumentation."""

from __future__ import annotations

import os
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

from mirascope import ops
from mirascope.ops._internal.instrumentation.providers.anthropic import (
    AnthropicInstrumentation,
)


@pytest.fixture(autouse=True)
def reset_instrumentation() -> Generator[None, None, None]:
    """Reset instrumentation state before and after each test."""
    AnthropicInstrumentation.reset_for_testing()
    yield
    AnthropicInstrumentation.reset_for_testing()


@pytest.fixture
def mock_anthropic_instrumentor() -> Generator[MagicMock, None, None]:
    """Mock the AnthropicInstrumentor class."""
    with patch(
        "mirascope.ops._internal.instrumentation.providers.anthropic.AnthropicInstrumentor"
    ) as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        yield mock_instance


def test_instrument_anthropic_basic(mock_anthropic_instrumentor: MagicMock) -> None:
    """Test basic instrumentation."""
    assert not ops.is_anthropic_instrumented()

    ops.instrument_anthropic()

    assert ops.is_anthropic_instrumented()
    mock_anthropic_instrumentor.instrument.assert_called_once_with()


def test_instrument_anthropic_idempotent(
    mock_anthropic_instrumentor: MagicMock,
) -> None:
    """Test that calling instrument_anthropic multiple times is idempotent."""
    ops.instrument_anthropic()
    ops.instrument_anthropic()
    ops.instrument_anthropic()

    mock_anthropic_instrumentor.instrument.assert_called_once()


def test_instrument_anthropic_with_tracer_provider(
    mock_anthropic_instrumentor: MagicMock,
) -> None:
    """Test instrumentation with a custom tracer provider."""
    mock_tracer_provider = MagicMock()

    ops.instrument_anthropic(tracer_provider=mock_tracer_provider)

    assert ops.is_anthropic_instrumented()
    mock_anthropic_instrumentor.instrument.assert_called_once_with(
        tracer_provider=mock_tracer_provider
    )


def test_instrument_anthropic_capture_content_enabled(
    mock_anthropic_instrumentor: MagicMock,
) -> None:
    """Test instrumentation with content capture enabled."""
    ops.instrument_anthropic(capture_content="enabled")

    assert os.environ.get("TRACELOOP_TRACE_CONTENT") == "true"


def test_instrument_anthropic_capture_content_disabled(
    mock_anthropic_instrumentor: MagicMock,
) -> None:
    """Test instrumentation with content capture disabled."""
    ops.instrument_anthropic(capture_content="disabled")

    assert os.environ.get("TRACELOOP_TRACE_CONTENT") == "false"


def test_uninstrument_anthropic(mock_anthropic_instrumentor: MagicMock) -> None:
    """Test uninstrumentation."""
    ops.instrument_anthropic()
    assert ops.is_anthropic_instrumented()

    ops.uninstrument_anthropic()
    assert not ops.is_anthropic_instrumented()
    mock_anthropic_instrumentor.uninstrument.assert_called_once()


def test_uninstrument_anthropic_when_not_instrumented() -> None:
    """Test that uninstrument_anthropic does nothing when not instrumented."""
    assert not ops.is_anthropic_instrumented()
    ops.uninstrument_anthropic()
    assert not ops.is_anthropic_instrumented()


def test_is_anthropic_instrumented_initial_state() -> None:
    """Test that is_anthropic_instrumented returns False initially."""
    assert not ops.is_anthropic_instrumented()


def test_instrument_anthropic_restores_env_on_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that environment variables are restored when instrument() fails."""
    # Clear env vars to ensure clean state
    monkeypatch.delenv("TRACELOOP_TRACE_CONTENT", raising=False)
    monkeypatch.delenv("OTEL_SEMCONV_STABILITY_OPT_IN", raising=False)

    with patch(
        "mirascope.ops._internal.instrumentation.providers.anthropic.AnthropicInstrumentor"
    ) as mock_cls:
        mock_instance = MagicMock()
        mock_instance.instrument.side_effect = RuntimeError("Instrumentation failed")
        mock_cls.return_value = mock_instance

        with pytest.raises(RuntimeError, match="Instrumentation failed"):
            ops.instrument_anthropic(capture_content="enabled")

    # All environment variables should be restored to original state (not set)
    assert os.environ.get("TRACELOOP_TRACE_CONTENT") is None
    assert os.environ.get("OTEL_SEMCONV_STABILITY_OPT_IN") is None
    assert not ops.is_anthropic_instrumented()


def test_instrument_anthropic_restores_existing_env_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that existing environment variable values are restored on uninstrument."""
    # Set existing values before instrumentation using monkeypatch
    monkeypatch.setenv("TRACELOOP_TRACE_CONTENT", "original_value")
    monkeypatch.setenv("OTEL_SEMCONV_STABILITY_OPT_IN", "original_semconv")

    with patch(
        "mirascope.ops._internal.instrumentation.providers.anthropic.AnthropicInstrumentor"
    ) as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance

        ops.instrument_anthropic(capture_content="enabled")

        # Values should be changed after instrumentation
        assert os.environ.get("TRACELOOP_TRACE_CONTENT") == "true"

        ops.uninstrument_anthropic()

    # Values should be restored to original
    assert os.environ.get("TRACELOOP_TRACE_CONTENT") == "original_value"
    assert os.environ.get("OTEL_SEMCONV_STABILITY_OPT_IN") == "original_semconv"
