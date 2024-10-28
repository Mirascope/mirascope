from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from mirascope.tools.search import DuckDuckGoSearch, DuckDuckGoSearchConfig


class SearchSchema(BaseModel):
    urls: list[str]


# Config Tests
def test_search_config_defaults():
    config = DuckDuckGoSearchConfig()
    assert config.max_results_per_query == 2


def test_search_config_custom():
    config = DuckDuckGoSearchConfig(max_results_per_query=5)
    assert config.max_results_per_query == 5


def test_search_config_from_env():
    config = DuckDuckGoSearchConfig.from_env()
    assert isinstance(config, DuckDuckGoSearchConfig)
    assert config.max_results_per_query == 2


def test_search_config_override():
    original = DuckDuckGoSearchConfig()
    override = DuckDuckGoSearchConfig(max_results_per_query=10)
    updated = original.override_defaults(override)
    assert updated.max_results_per_query == 10  # pyright: ignore [reportAttributeAccessIssue]


# Search Functionality Tests
@patch("mirascope.tools.search.duckduckgo.DDGS")
def test_single_query_success(mock_ddgs):
    mock_results = [{"href": "https://example1.com"}, {"href": "https://example2.com"}]
    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.text.return_value = mock_results
    mock_ddgs.return_value = mock_ddgs_instance

    search = DuckDuckGoSearch(queries=["test query"])
    result = search.call()

    assert "https://example1.com" in result
    assert "https://example2.com" in result
    mock_ddgs_instance.text.assert_called_once_with(
        "test query", max_results=search._config().max_results_per_query
    )


@patch("mirascope.tools.search.duckduckgo.DDGS")
def test_multiple_queries_success(mock_ddgs):
    mock_results = [{"href": "https://example1.com"}, {"href": "https://example2.com"}]
    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.text.return_value = mock_results
    mock_ddgs.return_value = mock_ddgs_instance

    search = DuckDuckGoSearch(queries=["query1", "query2"])
    result = search.call()

    assert "https://example1.com" in result
    assert "https://example2.com" in result
    assert mock_ddgs_instance.text.call_count == 2


@patch("mirascope.tools.search.duckduckgo.DDGS")
def test_empty_results(mock_ddgs):
    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.text.return_value = []
    mock_ddgs.return_value = mock_ddgs_instance

    search = DuckDuckGoSearch(queries=["test query"])
    result = search.call()

    assert result == ""


# Error Handling Tests
@patch("mirascope.tools.search.duckduckgo.DDGS")
def test_ddgs_initialization_error(mock_ddgs):
    mock_ddgs.side_effect = Exception("DDGS initialization failed")

    search = DuckDuckGoSearch(queries=["test query"])
    result = search.call()

    assert "Failed to search the web for text" in result


@patch("mirascope.tools.search.duckduckgo.DDGS")
def test_search_execution_error(mock_ddgs):
    mock_results = [{}, {"href": "https://example.com"}]
    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.text.return_value = mock_results
    mock_ddgs.return_value = mock_ddgs_instance

    search = DuckDuckGoSearch(queries=["test query"])
    result = search.call()

    assert "Failed to search the web for text" in result


@patch("mirascope.tools.search.duckduckgo.DDGS")
def test_url_parsing_error(mock_ddgs):
    mock_results = [
        {"href": None},  # Invalid URL
        {"href": "https://example.com"},  # Valid URL
    ]
    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.text.return_value = mock_results
    mock_ddgs.return_value = mock_ddgs_instance

    search = DuckDuckGoSearch(queries=["test query"])
    result = search.call()

    assert "<class 'TypeError'>: Failed to search the web for text" in result


# Custom Configuration Tests
@patch("mirascope.tools.search.duckduckgo.DDGS")
def test_custom_max_results(mock_ddgs):
    custom_config = DuckDuckGoSearchConfig(max_results_per_query=5)
    CustomSearch = DuckDuckGoSearch.from_config(custom_config)

    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.text.return_value = []
    mock_ddgs.return_value = mock_ddgs_instance

    search = CustomSearch(queries=["test query"])  # pyright: ignore [reportCallIssue]
    search.call()

    mock_ddgs_instance.text.assert_called_once_with("test query", max_results=5)


# Validation Tests
def test_none_queries():
    with pytest.raises(Exception):  # pydantic will raise validation error  # noqa: B017
        DuckDuckGoSearch(queries=None)  # pyright: ignore [reportArgumentType]


def test_invalid_query_type():
    with pytest.raises(Exception):  # pydantic will raise validation error  # noqa: B017
        DuckDuckGoSearch(queries=[123])  # type: ignore


# Integration Tests
def test_integration_with_search_tool_base():
    search = DuckDuckGoSearch(queries=["test"])
    instructions = search.get_prompt_instructions()

    assert "expert web searcher" in instructions
    assert "current date" in instructions
    assert search._name() in instructions
    assert search._description() in instructions
