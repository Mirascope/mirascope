"""Tests for the type_urls module and its integration with type_model and parser."""

from api2mdx.type_urls import BUILTIN_TYPE_URLS, get_doc_url_for_type


def test_get_doc_url_for_type() -> None:
    """Test the get_doc_url_for_type function."""
    # Test existing builtin types
    assert get_doc_url_for_type("str") == BUILTIN_TYPE_URLS["str"]
    assert get_doc_url_for_type("int") == BUILTIN_TYPE_URLS["int"]
    assert get_doc_url_for_type("list") == BUILTIN_TYPE_URLS["list"]

    # Test with quotes (which should be stripped)
    assert get_doc_url_for_type("'str'") == BUILTIN_TYPE_URLS["str"]
    assert get_doc_url_for_type('"int"') == BUILTIN_TYPE_URLS["int"]

    # Test non-existent type
    assert get_doc_url_for_type("NonExistentType") is None
