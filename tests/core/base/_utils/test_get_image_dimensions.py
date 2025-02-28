"""Tests for the get_image_dimensions function."""

import base64
from unittest.mock import MagicMock, patch

import pytest

from mirascope.core.base._utils import get_image_dimensions
from mirascope.core.base.types import ImageMetadata


@pytest.fixture
def mock_pil_image():
    """Fixture to create a mock PIL Image."""
    mock_image = MagicMock()
    mock_image.size = (100, 200)
    return mock_image


@pytest.fixture
def sample_base64_image():
    """Fixture to create a sample base64 image data URL."""
    # This is not actual image data, just a placeholder for testing
    fake_image_data = b"fake_image_data"
    base64_data = base64.b64encode(fake_image_data).decode("utf-8")
    return f"data:image/jpeg;base64,{base64_data}"


@patch("mirascope.core.base._utils._get_image_dimensions._load_media")
@patch("mirascope.core.base.types.Image.open")
@patch("mirascope.core.base.types.has_pil_module", True)
def test_http_url(mock_image_open, mock_load_media, mock_pil_image):
    """Test getting dimensions from an HTTP URL."""
    # Setup
    mock_load_media.return_value = b"binary_image_data"
    mock_image_instance = MagicMock()
    mock_image_instance.size = (800, 600)
    mock_image_open.return_value.__enter__.return_value = mock_image_instance

    # Execute
    result = get_image_dimensions("https://example.com/image.jpg")

    # Assert
    mock_load_media.assert_called_once_with("https://example.com/image.jpg")
    assert result == ImageMetadata(width=800, height=600)


@patch("mirascope.core.base.types.Image.open")
@patch("mirascope.core.base.types.has_pil_module", True)
def test_data_url(mock_image_open, sample_base64_image):
    """Test getting dimensions from a data URL."""
    # Setup
    mock_image_instance = MagicMock()
    mock_image_instance.size = (400, 300)
    mock_image_open.return_value.__enter__.return_value = mock_image_instance

    # Execute
    result = get_image_dimensions(sample_base64_image)

    # Assert
    mock_image_open.assert_called_once()
    assert result == ImageMetadata(width=400, height=300)


@patch("mirascope.core.base.types.has_pil_module", False)
@patch("mirascope.core.base._utils._get_image_dimensions._load_media")
def test_pil_not_available(mock_load_media):
    """Test behavior when PIL is not available."""
    # Setup
    mock_load_media.return_value = b"binary_image_data"

    # Execute
    result = get_image_dimensions("https://example.com/image.jpg")

    # Assert
    assert result is None


@patch("mirascope.core.base.types.Image.open")
@patch("mirascope.core.base.types.has_pil_module", True)
@patch("mirascope.core.base._utils._get_image_dimensions._load_media")
def test_exception_handling(mock_image_open, mock_load_media):
    """Test that exceptions are properly handled."""
    # Setup
    mock_load_media.side_effect = Exception("Network error")

    # Execute
    result = get_image_dimensions("https://example.com/image.jpg")

    # Assert
    assert result is None


@patch("mirascope.core.base.types.Image.open")
@patch("mirascope.core.base.types.has_pil_module", True)
def test_invalid_data_url(mock_image_open):
    """Test with invalid base64 data."""
    # Execute
    result = get_image_dimensions("data:image/jpeg;base64,!@#$%^")

    # Assert
    assert result is None


@pytest.fixture
def setup_pil_mock(monkeypatch, mock_pil_image):
    """Setup PIL mocks using pytest fixtures."""
    mock_open = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_pil_image
    monkeypatch.setattr("mirascope.core.base.types.Image.open", mock_open)
    monkeypatch.setattr("mirascope.core.base.types.has_pil_module", True)
    return mock_open


def test_with_pytest_fixtures(setup_pil_mock, sample_base64_image):
    """Test using pytest fixtures instead of unittest.patch."""
    # Execute
    result = get_image_dimensions(sample_base64_image)

    # Assert
    setup_pil_mock.assert_called_once()
    assert result == ImageMetadata(width=100, height=200)
