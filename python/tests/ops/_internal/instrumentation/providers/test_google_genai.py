"""Tests for Google GenAI provider instrumentation."""

from __future__ import annotations

import os
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

from mirascope import ops
from mirascope.ops._internal.instrumentation.providers.google_genai import (
    GoogleGenAIInstrumentation,
)


@pytest.fixture(autouse=True)
def reset_instrumentation() -> Generator[None, None, None]:
    """Reset instrumentation state before and after each test."""
    GoogleGenAIInstrumentation.reset_for_testing()
    yield
    GoogleGenAIInstrumentation.reset_for_testing()


@pytest.fixture
def mock_google_genai_instrumentor() -> Generator[MagicMock, None, None]:
    """Mock the GoogleGenAiSdkInstrumentor class."""
    with patch(
        "mirascope.ops._internal.instrumentation.providers.google_genai.GoogleGenAiSdkInstrumentor"
    ) as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        yield mock_instance


def test_instrument_google_genai_basic(
    mock_google_genai_instrumentor: MagicMock,
) -> None:
    """Test basic instrumentation."""
    assert not ops.is_google_genai_instrumented()

    ops.instrument_google_genai()

    assert ops.is_google_genai_instrumented()
    mock_google_genai_instrumentor.instrument.assert_called_once_with()


def test_instrument_google_genai_idempotent(
    mock_google_genai_instrumentor: MagicMock,
) -> None:
    """Test that calling instrument_google_genai multiple times is idempotent."""
    ops.instrument_google_genai()
    ops.instrument_google_genai()
    ops.instrument_google_genai()

    mock_google_genai_instrumentor.instrument.assert_called_once()


def test_instrument_google_genai_with_tracer_provider(
    mock_google_genai_instrumentor: MagicMock,
) -> None:
    """Test instrumentation with a custom tracer provider."""
    mock_tracer_provider = MagicMock()

    ops.instrument_google_genai(tracer_provider=mock_tracer_provider)

    assert ops.is_google_genai_instrumented()
    mock_google_genai_instrumentor.instrument.assert_called_once_with(
        tracer_provider=mock_tracer_provider
    )


def test_instrument_google_genai_capture_content_enabled(
    mock_google_genai_instrumentor: MagicMock,
) -> None:
    """Test instrumentation with content capture enabled."""
    ops.instrument_google_genai(capture_content="enabled")

    # Google GenAI uses SPAN_AND_EVENT instead of "true"
    assert (
        os.environ.get("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT")
        == "SPAN_AND_EVENT"
    )


def test_instrument_google_genai_capture_content_disabled(
    mock_google_genai_instrumentor: MagicMock,
) -> None:
    """Test instrumentation with content capture disabled."""
    ops.instrument_google_genai(capture_content="disabled")

    # Google GenAI uses NO_CONTENT instead of "false"
    assert (
        os.environ.get("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT")
        == "NO_CONTENT"
    )


def test_uninstrument_google_genai(mock_google_genai_instrumentor: MagicMock) -> None:
    """Test uninstrumentation."""
    ops.instrument_google_genai()
    assert ops.is_google_genai_instrumented()

    ops.uninstrument_google_genai()
    assert not ops.is_google_genai_instrumented()
    mock_google_genai_instrumentor.uninstrument.assert_called_once()


def test_uninstrument_google_genai_when_not_instrumented() -> None:
    """Test that uninstrument_google_genai does nothing when not instrumented."""
    assert not ops.is_google_genai_instrumented()
    ops.uninstrument_google_genai()
    assert not ops.is_google_genai_instrumented()


def test_is_google_genai_instrumented_initial_state() -> None:
    """Test that is_google_genai_instrumented returns False initially."""
    assert not ops.is_google_genai_instrumented()


def test_instrument_google_genai_restores_env_on_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that environment variables are restored when instrument() fails."""
    # Clear env vars to ensure clean state
    monkeypatch.delenv(
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", raising=False
    )
    monkeypatch.delenv("OTEL_SEMCONV_STABILITY_OPT_IN", raising=False)

    with patch(
        "mirascope.ops._internal.instrumentation.providers.google_genai.GoogleGenAiSdkInstrumentor"
    ) as mock_cls:
        mock_instance = MagicMock()
        mock_instance.instrument.side_effect = RuntimeError("Instrumentation failed")
        mock_cls.return_value = mock_instance

        with pytest.raises(RuntimeError, match="Instrumentation failed"):
            ops.instrument_google_genai(capture_content="enabled")

    # All environment variables should be restored to original state (not set)
    assert os.environ.get("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT") is None
    assert os.environ.get("OTEL_SEMCONV_STABILITY_OPT_IN") is None
    assert not ops.is_google_genai_instrumented()


def test_instrument_google_genai_restores_existing_env_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that existing environment variable values are restored on uninstrument."""
    # Set existing values before instrumentation using monkeypatch
    monkeypatch.setenv(
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "original_value"
    )
    monkeypatch.setenv("OTEL_SEMCONV_STABILITY_OPT_IN", "original_semconv")

    with patch(
        "mirascope.ops._internal.instrumentation.providers.google_genai.GoogleGenAiSdkInstrumentor"
    ) as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance

        ops.instrument_google_genai(capture_content="enabled")

        # Values should be changed after instrumentation
        assert (
            os.environ.get("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT")
            == "SPAN_AND_EVENT"
        )

        ops.uninstrument_google_genai()

    # Values should be restored to original
    assert (
        os.environ.get("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT")
        == "original_value"
    )
    assert os.environ.get("OTEL_SEMCONV_STABILITY_OPT_IN") == "original_semconv"
