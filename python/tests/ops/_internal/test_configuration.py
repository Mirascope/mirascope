"""Tests for the configuration module."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from opentelemetry.sdk.trace import TracerProvider

from mirascope import ops
from mirascope.ops._internal import configuration

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture
def mock_mirascope_client() -> Generator[MagicMock, None, None]:
    """Mock the Mirascope client to avoid actual API calls."""
    with patch("mirascope.ops._internal.configuration.Mirascope") as mock:
        mock.return_value = MagicMock()
        yield mock


@pytest.fixture
def mock_exporter() -> Generator[MagicMock, None, None]:
    """Mock the MirascopeOTLPExporter at the re-export location."""
    with patch("mirascope.ops._internal.configuration.MirascopeOTLPExporter") as mock:
        mock.return_value = MagicMock()
        yield mock


def test_configure_with_tracer_provider() -> None:
    """Configure the SDK with a custom tracer provider."""
    tracer_provider = TracerProvider()
    ops.configure(tracer_provider=tracer_provider)
    assert configuration._tracer_provider is tracer_provider  # pyright: ignore[reportPrivateUsage]
    assert configuration._tracer is not None  # pyright: ignore[reportPrivateUsage]


def test_configure_with_api_key(
    mock_mirascope_client: MagicMock, mock_exporter: MagicMock
) -> None:
    """Configure with explicit API key auto-creates Mirascope Cloud provider."""
    ops.configure(api_key="test-api-key", base_url="test-base-url")

    mock_mirascope_client.assert_called_once_with(
        api_key="test-api-key", base_url="test-base-url"
    )
    mock_exporter.assert_called_once()
    assert configuration._tracer_provider is not None  # pyright: ignore[reportPrivateUsage]
    assert configuration._tracer is not None  # pyright: ignore[reportPrivateUsage]


def test_configure_with_env_api_key(
    mock_mirascope_client: MagicMock, mock_exporter: MagicMock
) -> None:
    """Configure with MIRASCOPE_API_KEY env var auto-creates Mirascope Cloud provider."""
    original_value = os.environ.get("MIRASCOPE_API_KEY")
    os.environ["MIRASCOPE_API_KEY"] = "env-api-key"
    try:
        ops.configure()

        mock_mirascope_client.assert_called_once_with(api_key=None, base_url=None)
        mock_exporter.assert_called_once()
        assert configuration._tracer_provider is not None  # pyright: ignore[reportPrivateUsage]
        assert configuration._tracer is not None  # pyright: ignore[reportPrivateUsage]
    finally:
        if original_value is not None:
            os.environ["MIRASCOPE_API_KEY"] = original_value
        else:
            os.environ.pop("MIRASCOPE_API_KEY", None)


def test_configure_without_credentials_raises() -> None:
    """Configure without API key or tracer_provider raises RuntimeError."""
    os.environ.pop("MIRASCOPE_API_KEY", None)

    with pytest.raises(RuntimeError, match="Failed to create Mirascope Cloud client"):
        ops.configure()


def test_configure_with_custom_tracer_name(
    mock_mirascope_client: MagicMock, mock_exporter: MagicMock
) -> None:
    """Configure with custom tracer name."""
    ops.configure(api_key="test-key", tracer_name="custom.tracer")

    assert configuration._tracer_name == "custom.tracer"  # pyright: ignore[reportPrivateUsage]


def test_configure_with_tracer_version(
    mock_mirascope_client: MagicMock, mock_exporter: MagicMock
) -> None:
    """Configure with tracer version."""
    ops.configure(api_key="test-key", tracer_version="1.0.0")

    assert configuration._tracer_version == "1.0.0"  # pyright: ignore[reportPrivateUsage]


def test_configure_tracer_provider_takes_precedence(
    mock_mirascope_client: MagicMock,
) -> None:
    """When tracer_provider is given, it takes precedence over api_key."""
    custom_provider = TracerProvider()
    ops.configure(tracer_provider=custom_provider, api_key="ignored-key")

    # Mirascope client should NOT be created when tracer_provider is given
    mock_mirascope_client.assert_not_called()
    assert configuration._tracer_provider is custom_provider  # pyright: ignore[reportPrivateUsage]


def test_create_mirascope_cloud_provider_success(
    mock_mirascope_client: MagicMock, mock_exporter: MagicMock
) -> None:
    """_create_mirascope_cloud_provider creates provider successfully."""
    provider = configuration._create_mirascope_cloud_provider(  # pyright: ignore[reportPrivateUsage]
        api_key="test-key", base_url="test-base-url"
    )

    assert isinstance(provider, TracerProvider)
    mock_mirascope_client.assert_called_once_with(
        api_key="test-key", base_url="test-base-url"
    )
    mock_exporter.assert_called_once()


def test_create_mirascope_cloud_provider_no_api_key() -> None:
    """_create_mirascope_cloud_provider raises when no API key available."""
    os.environ.pop("MIRASCOPE_API_KEY", None)

    with pytest.raises(RuntimeError, match="Failed to create Mirascope Cloud client"):
        configuration._create_mirascope_cloud_provider()  # pyright: ignore[reportPrivateUsage]


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
