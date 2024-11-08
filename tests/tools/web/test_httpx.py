from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from mirascope.tools.web._httpx import (
    HTTPX,
    AsyncHTTPX,
    HTTPXConfig,
)


def test_httpx_config():
    """Test HTTPXConfig initialization and default values"""
    config = HTTPXConfig()
    assert config.timeout == 5

    custom_config = HTTPXConfig(timeout=10)
    assert custom_config.timeout == 10


def test_async_httpx_config():
    """Test AsyncHTTPXConfig initialization and default values"""
    config = HTTPXConfig()
    assert config.timeout == 5

    custom_config = HTTPXConfig(timeout=10)
    assert custom_config.timeout == 10


@patch("mirascope.tools.web._httpx.httpx.Client")
def test_httpx_get_success(mock_client):
    """Test successful GET request using HTTPX"""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.text = "Test content"
    mock_client_instance = MagicMock()
    mock_client_instance.request.return_value = mock_response
    mock_client.return_value.__enter__.return_value = mock_client_instance

    # Make request
    tool = HTTPX(url="https://example.com")  # pyright: ignore [reportCallIssue]
    result = tool.call()

    # Assert results
    assert result == "Test content"
    mock_client_instance.request.assert_called_with(
        method="GET",
        url="https://example.com",
        params=None,
        json=None,
        data=None,
        headers=None,
        follow_redirects=True,
    )


@patch("mirascope.tools.web._httpx.httpx.Client")
def test_httpx_post_with_json(mock_client):
    """Test POST request with JSON data using HTTPX"""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.text = "Test response"
    mock_client_instance = MagicMock()
    mock_client_instance.request.return_value = mock_response
    mock_client.return_value.__enter__.return_value = mock_client_instance

    # Make request
    tool = HTTPX(  # pyright: ignore [reportCallIssue]
        url="https://example.com",
        method="POST",
        json={"key": "value"},
        headers={"Content-Type": "application/json"},
        follow_redirects=False,
    )
    result = tool.call()

    # Assert results
    assert result == "Test response"
    mock_client_instance.request.assert_called_with(
        method="POST",
        url="https://example.com",
        params=None,
        json={"key": "value"},
        data=None,
        headers={"Content-Type": "application/json"},
        follow_redirects=False,
    )


@patch("mirascope.tools.web._httpx.httpx.Client")
def test_httpx_request_error(mock_client):
    """Test handling of RequestError in HTTPX"""
    mock_client_instance = MagicMock()
    mock_client_instance.request.side_effect = httpx.RequestError("Connection failed")
    mock_client.return_value.__enter__.return_value = mock_client_instance

    tool = HTTPX(url="https://example.com")  # pyright: ignore [reportCallIssue]
    result = tool.call()
    assert "Request error occurred" in result


@patch("mirascope.tools.web._httpx.httpx.Client")
def test_httpx_http_error(mock_client):
    """Test handling of HTTPStatusError in HTTPX"""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not Found", request=MagicMock(), response=mock_response
    )
    mock_client_instance = MagicMock()
    mock_client_instance.request.return_value = mock_response
    mock_client.return_value.__enter__.return_value = mock_client_instance

    tool = HTTPX(url="https://example.com")  # pyright: ignore [reportCallIssue]
    result = tool.call()
    assert "HTTP error occurred: 404" in result


@patch("mirascope.tools.web._httpx.httpx.Client")
def test_httpx_value_error(mock_client):
    """Test handling of HTTPStatusError in HTTPX"""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = ValueError("Not Found")
    mock_client_instance = MagicMock()
    mock_client_instance.request.return_value = mock_response
    mock_client.return_value.__enter__.return_value = mock_client_instance

    tool = HTTPX(url="https://example.com")  # pyright: ignore [reportCallIssue]
    tool.call()
    assert "ValueError: Failed to make request to https://example.com"


@pytest.mark.asyncio
@patch("mirascope.tools.web._httpx.httpx.AsyncClient")
async def test_async_httpx_get_success(mock_client):
    """Test successful GET request using AsyncHTTPX"""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.text = "Test content"
    mock_client_instance = AsyncMock()
    mock_client_instance.request.return_value = mock_response
    mock_client.return_value.__aenter__.return_value = mock_client_instance

    # Make request
    tool = AsyncHTTPX(url="https://example.com")  # pyright: ignore [reportCallIssue]
    result = await tool.call()

    # Assert results
    assert result == "Test content"
    mock_client_instance.request.assert_called_with(
        method="GET",
        url="https://example.com",
        params=None,
        json=None,
        data=None,
        headers=None,
        follow_redirects=True,
    )


@pytest.mark.asyncio
@patch("mirascope.tools.web._httpx.httpx.AsyncClient")
async def test_async_httpx_post_with_json(mock_client):
    """Test POST request with JSON data using AsyncHTTPX"""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.text = "Test response"
    mock_client_instance = AsyncMock()
    mock_client_instance.request.return_value = mock_response
    mock_client.return_value.__aenter__.return_value = mock_client_instance

    # Make request
    tool = AsyncHTTPX(  # pyright: ignore [reportCallIssue]
        url="https://example.com",
        method="POST",
        json={"key": "value"},
        headers={"Content-Type": "application/json"},
        follow_redirects=False,
    )
    result = await tool.call()

    # Assert results
    assert result == "Test response"
    mock_client_instance.request.assert_called_with(
        method="POST",
        url="https://example.com",
        params=None,
        json={"key": "value"},
        data=None,
        headers={"Content-Type": "application/json"},
        follow_redirects=False,
    )


@pytest.mark.asyncio
@patch("mirascope.tools.web._httpx.httpx.AsyncClient")
async def test_async_httpx_request_error(mock_client):
    """Test handling of RequestError in AsyncHTTPX"""
    mock_client_instance = AsyncMock()
    mock_client_instance.request.side_effect = httpx.RequestError("Connection failed")
    mock_client.return_value.__aenter__.return_value = mock_client_instance

    tool = AsyncHTTPX(url="https://example.com")  # pyright: ignore [reportCallIssue]
    result = await tool.call()
    assert "Request error occurred" in result


@pytest.mark.asyncio
@patch("mirascope.tools.web._httpx.httpx.AsyncClient")
async def test_async_httpx_http_error(mock_client):
    """Test handling of HTTPStatusError in AsyncHTTPX"""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not Found", request=MagicMock(), response=mock_response
    )
    mock_client_instance = AsyncMock()
    mock_client_instance.request.return_value = mock_response
    mock_client.return_value.__aenter__.return_value = mock_client_instance

    tool = AsyncHTTPX(url="https://example.com")  # pyright: ignore [reportCallIssue]
    result = await tool.call()
    assert "HTTP error occurred: 404 - Not Found" in result


@pytest.mark.asyncio
@patch("mirascope.tools.web._httpx.httpx.AsyncClient")
async def test_async_httpx_value_error(mock_client):
    """Test handling of HTTPStatusError in AsyncHTTPX"""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = ValueError("Not Found")
    mock_client_instance = AsyncMock()
    mock_client_instance.request.return_value = mock_response
    mock_client.return_value.__aenter__.return_value = mock_client_instance

    tool = AsyncHTTPX(url="https://example.com")  # pyright: ignore [reportCallIssue]
    result = await tool.call()
    assert "ValueError: Failed to make request to https://example.com" in result
