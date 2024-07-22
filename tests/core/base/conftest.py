"""Shared fixtures for the base module tests."""

from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture()
def mock_setup_call() -> MagicMock:
    """Returns the mock setup_call function."""
    mock_setup_call = MagicMock()
    mock_setup_call.return_value = tuple([MagicMock() for _ in range(5)])
    return mock_setup_call


@pytest.fixture()
def mock_setup_call_async() -> MagicMock:
    """Returns the mock setup_call function."""
    mock_setup_call = MagicMock()
    mock_setup_call.return_value = tuple(
        [AsyncMock()] + [MagicMock() for _ in range(4)]
    )
    return mock_setup_call
