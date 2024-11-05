from unittest.mock import MagicMock, patch

import requests

from mirascope.tools import ParseURLConfig, ParseURLContent


# Config Tests
def test_parse_config_defaults():
    config = ParseURLConfig()  # pyright: ignore [reportCallIssue]
    assert config.parser == "html.parser"
    assert config.timeout == 5


def test_parse_config_custom():
    config = ParseURLConfig(parser="lxml", timeout=10)
    assert config.parser == "lxml"
    assert config.timeout == 10


def test_parse_config_from_env():
    config = ParseURLConfig.from_env()
    assert isinstance(config, ParseURLConfig)
    assert config.parser == "html.parser"
    assert config.timeout == 5


# URL Fetch Tests
@patch("mirascope.tools.web._parse_url_content.requests.get")
def test_successful_fetch_and_parse(mock_get):
    mock_response = MagicMock()
    mock_response.text = """
        <html>
            <body>
                <main>
                    <p>Main content</p>
                </main>
            </body>
        </html>
    """
    mock_get.return_value = mock_response

    tool = ParseURLContent(url="https://example.com")
    result = tool.call()

    assert "Main content" in result
    mock_get.assert_called_once_with("https://example.com", timeout=5)


@patch("mirascope.tools.web._parse_url_content.requests.get")
def test_fetch_with_custom_config(mock_get):
    mock_response = MagicMock()
    mock_response.text = "<html><body>Test</body></html>"
    mock_get.return_value = mock_response

    custom_config = ParseURLConfig(timeout=10)  # pyright: ignore [reportCallIssue]
    CustomTool = ParseURLContent.from_config(custom_config)
    tool = CustomTool(url="https://example.com")  # pyright: ignore [reportCallIssue]
    tool.call()

    mock_get.assert_called_once_with("https://example.com", timeout=10)


@patch("mirascope.tools.web._parse_url_content.requests.get")
def test_request_exception(mock_get):
    mock_get.side_effect = requests.RequestException("Connection error")

    tool = ParseURLContent(url="https://example.com")
    result = tool.call()

    assert "Failed to fetch content from URL: Connection error" in result


# Content Parsing Tests
@patch("mirascope.tools.web._parse_url_content.requests.get")
def test_parse_main_content(mock_get):
    mock_response = MagicMock()
    mock_response.text = """
        <html>
            <script>alert('test')</script>
            <header>Header</header>
            <main>
                <h1>Main Title</h1>
                <p>Main content</p>
            </main>
            <footer>Footer</footer>
        </html>
    """
    mock_get.return_value = mock_response

    tool = ParseURLContent(url="https://example.com")
    result = tool.call()

    assert "Main Title" in result
    assert "Main content" in result
    assert "alert" not in result
    assert "Header" not in result
    assert "Footer" not in result


@patch("mirascope.tools.web._parse_url_content.requests.get")
def test_parse_article_content(mock_get):
    mock_response = MagicMock()
    mock_response.text = """
        <html>
            <body>
                <article>
                    <h1>Article Title</h1>
                    <p>Article content</p>
                </article>
            </body>
        </html>
    """
    mock_get.return_value = mock_response

    tool = ParseURLContent(url="https://example.com")
    result = tool.call()

    assert "Article Title" in result
    assert "Article content" in result


@patch("mirascope.tools.web._parse_url_content.requests.get")
def test_parse_div_content(mock_get):
    mock_response = MagicMock()
    mock_response.text = """
        <html>
            <body>
                <div class="main-content">
                    <h1>Content Title</h1>
                    <p>Content text</p>
                </div>
            </body>
        </html>
    """
    mock_get.return_value = mock_response

    tool = ParseURLContent(url="https://example.com")
    result = tool.call()

    assert "Content Title" in result
    assert "Content text" in result


@patch("mirascope.tools.web._parse_url_content.requests.get")
def test_no_main_content(mock_get):
    mock_response = MagicMock()
    mock_response.text = """
        <html>
            <body>
                <div>
                    <p>Regular content</p>
                </div>
            </body>
        </html>
    """
    mock_get.return_value = mock_response

    tool = ParseURLContent(url="https://example.com")
    result = tool.call()

    assert "Regular content" in result


@patch("mirascope.tools.web._parse_url_content.requests.get")
def test_empty_content(mock_get):
    mock_response = MagicMock()
    mock_response.text = "<html><body></body></html>"
    mock_get.return_value = mock_response

    tool = ParseURLContent(url="https://example.com")
    result = tool.call()

    assert "No content found on the page" in result


@patch("mirascope.tools.web._parse_url_content.requests.get")
def test_http_error(mock_get):
    mock_get.side_effect = requests.RequestException("404 Client Error")

    tool = ParseURLContent(url="https://example.com")
    result = tool.call()

    assert "Failed to fetch content from URL" in result


@patch("mirascope.tools.web._parse_url_content.requests.get")
def test_multiline_content(mock_get):
    mock_response = MagicMock()
    mock_response.text = """
        <html>
            <main>
                <p>First line</p>
                <p>Second line</p>
                <p>Third line</p>
            </main>
        </html>
    """
    mock_get.return_value = mock_response

    tool = ParseURLContent(url="https://example.com")
    result = tool.call()

    assert "First line" in result
    assert "Second line" in result
    assert "Third line" in result
