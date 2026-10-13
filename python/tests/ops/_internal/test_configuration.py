"""Tests for the configuration module."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from opentelemetry.sdk.trace import TracerProvider

from mirascope import ops
from mirascope.ops._internal import configuration


def test_configure_with_tracer_provider() -> None:
    """Configure the SDK with a custom tracer provider."""
    tracer_provider = TracerProvider()
    ops.configure(tracer_provider=tracer_provider)
    assert configuration._tracer_provider is tracer_provider  # pyright: ignore[reportPrivateUsage]
    assert configuration._tracer is not None  # pyright: ignore[reportPrivateUsage]


def test_configure_with_custom_tracer_name() -> None:
    """Configure with custom tracer name."""
    tracer_provider = TracerProvider()
    ops.configure(tracer_provider=tracer_provider, tracer_name="custom.tracer")

    assert configuration._tracer_name == "custom.tracer"  # pyright: ignore[reportPrivateUsage]


def test_configure_with_tracer_version() -> None:
    """Configure with tracer version."""
    tracer_provider = TracerProvider()
    ops.configure(tracer_provider=tracer_provider, tracer_version="1.0.0")

    assert configuration._tracer_version == "1.0.0"  # pyright: ignore[reportPrivateUsage]


def test_set_tracer() -> None:
    """set_tracer sets the tracer."""
    mock_tracer = MagicMock()
    configuration.set_tracer(mock_tracer)

    assert configuration._tracer is mock_tracer  # pyright: ignore[reportPrivateUsage]


def test_get_tracer() -> None:
    """get_tracer returns the configured tracer."""
    mock_tracer = MagicMock()
    configuration._tracer = mock_tracer  # pyright: ignore[reportPrivateUsage]

    assert configuration.get_tracer() is mock_tracer


def test_get_tracer_returns_none_when_not_configured() -> None:
    """get_tracer returns None when not configured."""
    configuration._tracer = None  # pyright: ignore[reportPrivateUsage]

    assert configuration.get_tracer() is None


def test_tracer_context() -> None:
    """tracer_context temporarily sets a different tracer."""
    original_tracer = MagicMock(name="original")
    new_tracer = MagicMock(name="new")

    configuration.set_tracer(original_tracer)
    assert configuration.get_tracer() is original_tracer

    with configuration.tracer_context(new_tracer) as ctx_tracer:
        assert ctx_tracer is new_tracer
        assert configuration.get_tracer() is new_tracer

    # Original tracer is restored
    assert configuration.get_tracer() is original_tracer


def test_tracer_context_restores_on_exception() -> None:
    """tracer_context restores original tracer even if exception occurs."""
    original_tracer = MagicMock(name="original")
    new_tracer = MagicMock(name="new")

    configuration.set_tracer(original_tracer)

    with (
        pytest.raises(ValueError, match="test error"),
        configuration.tracer_context(new_tracer),
    ):
        assert configuration.get_tracer() is new_tracer
        raise ValueError("test error")

    # Original tracer is still restored
    assert configuration.get_tracer() is original_tracer
