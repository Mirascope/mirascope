from unittest.mock import MagicMock, patch

from mirascope.tools import Requests, RequestsConfig


def test_requests_config():
    config = RequestsConfig()
    assert config.timeout == 5

    custom_config = RequestsConfig(timeout=10)
    assert custom_config.timeout == 10


@patch("mirascope.tools.web._requests.requests")
def test_requests_get_success(mock_request):
    mock_response = MagicMock()
    mock_response.text = "Test content"
    mock_request.request.return_value = mock_response

    tool = Requests(url="https://example.com")  # pyright: ignore [reportCallIssue]
    result = tool.call()

    assert result == "Test content"
    mock_request.request.assert_called_with(
        method="GET",
        url="https://example.com",
        json=None,
        headers=None,
        timeout=tool._get_config().timeout,
    )


@patch("mirascope.tools.web._requests.requests")
def test_requests_post_with_data(mock_request):
    mock_response = MagicMock()
    mock_response.text = "Test response"
    mock_request.request.return_value = mock_response

    tool = Requests(
        url="https://example.com",
        method="POST",
        data={"key": "value"},
        headers={"Content-Type": "application/json"},
    )
    result = tool.call()

    assert result == "Test response"
    mock_request.request.assert_called_with(
        method="POST",
        url="https://example.com",
        json={"key": "value"},
        headers={"Content-Type": "application/json"},
        timeout=tool._get_config().timeout,
    )


@patch("mirascope.tools.web._requests.requests")
def test_requests_error(mock_request):
    mock_request.request.side_effect = Exception("Request failed")

    tool = Requests(url="https://example.com")  # pyright: ignore [reportCallIssue]
    result = tool.call()
    assert "Failed to extract content from URL" in result
