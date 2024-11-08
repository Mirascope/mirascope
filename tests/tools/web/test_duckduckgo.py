from unittest.mock import AsyncMock, MagicMock, patch

from pydantic import BaseModel
from pytest import mark

from mirascope.tools.web._duckduckgo import (
    AsyncDuckDuckGoSearch,
    DuckDuckGoSearch,
    DuckDuckGoSearchConfig,
)


class SearchSchema(BaseModel):
    """Schema for search results"""

    urls: list[str]


# Config Tests
def test_search_config_defaults():
    """Test default configuration values"""
    config = DuckDuckGoSearchConfig()
    assert config.max_results_per_query == 2


def test_search_config_custom():
    """Test setting custom configuration values"""
    config = DuckDuckGoSearchConfig(max_results_per_query=5)
    assert config.max_results_per_query == 5


def test_search_config_from_env():
    """Test loading configuration from environment variables"""
    config = DuckDuckGoSearchConfig.from_env()
    assert isinstance(config, DuckDuckGoSearchConfig)
    assert config.max_results_per_query == 2


# Search Functionality Tests
@patch("mirascope.tools.web._duckduckgo.DDGS")
def test_single_query_success(mock_ddgs):
    """Test successful execution of a single search query"""
    mock_results = [
        {
            "title": "Example Site 1",
            "href": "https://example1.com",
            "body": "This is the first example snippet",
        },
        {
            "title": "Example Site 2",
            "href": "https://example2.com",
            "body": "This is the second example snippet",
        },
    ]
    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.text.return_value = mock_results
    mock_ddgs.return_value = mock_ddgs_instance

    search = DuckDuckGoSearch(queries=["test query"])
    result = search.call()

    assert "Example Site 1" in result
    assert "https://example1.com" in result
    assert "This is the first example snippet" in result
    mock_ddgs_instance.text.assert_called_once_with(
        "test query", max_results=search._get_config().max_results_per_query
    )


@patch("mirascope.tools.web._duckduckgo.DDGS")
def test_multiple_queries_success(mock_ddgs):
    """Test successful execution of multiple search queries"""
    mock_results = [
        {
            "title": "Multiple Query Result 1",
            "href": "https://example1.com",
            "body": "First query result snippet",
        },
        {
            "title": "Multiple Query Result 2",
            "href": "https://example2.com",
            "body": "Second query result snippet",
        },
    ]
    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.text.return_value = mock_results
    mock_ddgs.return_value = mock_ddgs_instance

    search = DuckDuckGoSearch(queries=["query1", "query2"])
    result = search.call()

    assert "Multiple Query Result 1" in result
    assert "https://example1.com" in result
    assert "First query result snippet" in result
    assert mock_ddgs_instance.text.call_count == 2


@patch("mirascope.tools.web._duckduckgo.DDGS")
def test_empty_results(mock_ddgs):
    """Test handling of empty search results"""
    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.text.return_value = []
    mock_ddgs.return_value = mock_ddgs_instance

    search = DuckDuckGoSearch(queries=["test query"])
    result = search.call()

    assert result == ""


# Error Handling Tests
@patch("mirascope.tools.web._duckduckgo.DDGS")
def test_ddgs_initialization_error(mock_ddgs):
    """Test error handling during DDGS initialization"""
    mock_ddgs.side_effect = Exception("DDGS initialization failed")

    search = DuckDuckGoSearch(queries=["test query"])
    result = search.call()

    assert "<class 'Exception'>: Failed to search the web for text" in result


@patch("mirascope.tools.web._duckduckgo.DDGS")
def test_search_execution_error(mock_ddgs):
    """Test error handling during search execution"""
    mock_results = [
        {
            "title": "Error Test",
            "href": None,
            "body": "Test snippet",
        }
    ]
    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.text.return_value = mock_results
    mock_ddgs.return_value = mock_ddgs_instance

    search = DuckDuckGoSearch(queries=["test query"])
    result = search.call()

    assert "Title: Error Test\nURL: None\nSnippet: Test snippet" in result


@patch("mirascope.tools.web._duckduckgo.DDGS")
def test_url_parsing_error(mock_ddgs):
    """Test error handling during URL parsing"""
    mock_results = [
        {
            "title": "Invalid URL Test",
            "href": None,
            "body": "Test snippet with invalid URL",
        },
        {
            "title": "Valid URL Test",
            "href": "https://example.com",
            "body": "Test snippet with valid URL",
        },
    ]
    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.text.return_value = mock_results
    mock_ddgs.return_value = mock_ddgs_instance

    search = DuckDuckGoSearch(queries=["test query"])
    result = search.call()

    assert (
        "Title: Invalid URL Test\n"
        "URL: None\n"
        "Snippet: Test snippet with invalid URL\n"
        "\n"
        "Title: Valid URL Test\n"
        "URL: https://example.com\n"
        "Snippet: Test snippet with valid URL"
    ) in result


# Custom Configuration Tests
@patch("mirascope.tools.web._duckduckgo.DDGS")
def test_custom_max_results(mock_ddgs):
    """Test using custom maximum results configuration"""

    # Create new search class with custom config
    CustomSearch = DuckDuckGoSearch.from_config(
        DuckDuckGoSearchConfig(max_results_per_query=5)
    )

    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.text.return_value = []
    mock_ddgs.return_value = mock_ddgs_instance

    search = CustomSearch(queries=["test query"])  # pyright: ignore [reportCallIssue]
    search.call()

    mock_ddgs_instance.text.assert_called_once_with("test query", max_results=5)


# Integration Tests
def test_integration_with_search_tool_base():
    """Test integration with search tool base class"""
    search = DuckDuckGoSearch(queries=["test"])
    description = search.usage_description()

    assert isinstance(description, str)
    assert len(description) > 0


# Async Search Functionality Tests
@mark.asyncio
@patch("mirascope.tools.web._duckduckgo.AsyncDDGS")
async def test_async_single_query_success(mock_async_ddgs):
    """Test successful execution of a single async search query"""
    mock_results = [
        {
            "title": "Async Example 1",
            "href": "https://example1.com",
            "body": "First async test snippet",
        },
        {
            "title": "Async Example 2",
            "href": "https://example2.com",
            "body": "Second async test snippet",
        },
    ]
    mock_ddgs_instance = AsyncMock()
    mock_ddgs_instance.atext.return_value = mock_results
    mock_async_ddgs.return_value = mock_ddgs_instance

    search = AsyncDuckDuckGoSearch(queries=["test query"])
    result = await search.call()

    assert "Async Example 1" in result
    assert "https://example1.com" in result
    assert "First async test snippet" in result
    mock_ddgs_instance.atext.assert_called_once_with(
        "test query", max_results=search._get_config().max_results_per_query
    )


@mark.asyncio
@patch("mirascope.tools.web._duckduckgo.AsyncDDGS")
async def test_async_multiple_queries_success(mock_async_ddgs):
    """Test successful execution of multiple async search queries"""
    mock_results = [
        {
            "title": "Async Multiple Result 1",
            "href": "https://example1.com",
            "body": "First async query result",
        },
        {
            "title": "Async Multiple Result 2",
            "href": "https://example2.com",
            "body": "Second async query result",
        },
    ]
    mock_ddgs_instance = AsyncMock()
    mock_ddgs_instance.atext.return_value = mock_results
    mock_async_ddgs.return_value = mock_ddgs_instance

    search = AsyncDuckDuckGoSearch(queries=["query1", "query2"])
    result = await search.call()

    assert "Async Multiple Result 1" in result
    assert "https://example1.com" in result
    assert mock_ddgs_instance.atext.call_count == 2


@mark.asyncio
@patch("mirascope.tools.web._duckduckgo.AsyncDDGS")
async def test_async_empty_results(mock_async_ddgs):
    """Test handling of empty async search results"""
    mock_ddgs_instance = AsyncMock()
    mock_ddgs_instance.atext.return_value = []
    mock_async_ddgs.return_value = mock_ddgs_instance

    search = AsyncDuckDuckGoSearch(queries=["test query"])
    result = await search.call()

    assert result == ""


# Async Error Handling Tests
@mark.asyncio
@patch("mirascope.tools.web._duckduckgo.AsyncDDGS")
async def test_async_ddgs_initialization_error(mock_async_ddgs):
    """Test error handling during async DDGS initialization"""
    mock_async_ddgs.side_effect = Exception("AsyncDDGS initialization failed")

    search = AsyncDuckDuckGoSearch(queries=["test query"])
    result = await search.call()

    assert "Failed to search the web for text" in result


@mark.asyncio
@patch("mirascope.tools.web._duckduckgo.AsyncDDGS")
async def test_async_search_execution_error(mock_async_ddgs):
    """Test error handling during async search execution"""
    mock_ddgs_instance = AsyncMock()
    mock_ddgs_instance.atext.side_effect = Exception("Search execution failed")
    mock_async_ddgs.return_value = mock_ddgs_instance

    search = AsyncDuckDuckGoSearch(queries=["test query"])
    result = await search.call()

    assert "Failed to search the web for text" in result


@mark.asyncio
@patch("mirascope.tools.web._duckduckgo.AsyncDDGS")
async def test_async_url_parsing_error(mock_async_ddgs):
    """Test error handling during async URL parsing"""
    mock_results = [
        {
            "title": "Async Invalid URL",
            "href": None,
            "body": "Test async snippet with invalid URL",
        },
        {
            "title": "Async Valid URL",
            "href": "https://example.com",
            "body": "Test async snippet with valid URL",
        },
    ]
    mock_ddgs_instance = AsyncMock()
    mock_ddgs_instance.atext.return_value = mock_results
    mock_async_ddgs.return_value = mock_ddgs_instance

    search = AsyncDuckDuckGoSearch(queries=["test query"])
    result = await search.call()

    assert (
        "Title: Async Invalid URL\n"
        "URL: None\n"
        "Snippet: Test async snippet with invalid URL\n"
        "\n"
        "Title: Async Valid URL\n"
        "URL: https://example.com\n"
        "Snippet: Test async snippet with valid URL"
    ) in result


# Async Custom Configuration Tests
@mark.asyncio
@patch("mirascope.tools.web._duckduckgo.AsyncDDGS")
async def test_async_custom_max_results(mock_async_ddgs):
    """Test using custom maximum results configuration in async search"""
    custom_config = DuckDuckGoSearchConfig(max_results_per_query=5)
    CustomAsyncSearch = AsyncDuckDuckGoSearch.from_config(custom_config)

    mock_ddgs_instance = AsyncMock()
    mock_ddgs_instance.atext.return_value = []
    mock_async_ddgs.return_value = mock_ddgs_instance

    search = CustomAsyncSearch(queries=["test query"])  # pyright: ignore [reportCallIssue]
    await search.call()

    mock_ddgs_instance.atext.assert_called_once_with("test query", max_results=5)


# Async Integration Tests
@mark.asyncio
async def test_async_integration_with_search_tool_base():
    """Test integration with async search tool base class"""
    search = AsyncDuckDuckGoSearch(queries=["test"])
    description = search.usage_description()

    assert isinstance(description, str)
    assert len(description) > 0
