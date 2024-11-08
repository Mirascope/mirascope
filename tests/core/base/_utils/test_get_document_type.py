"""Tests the `_utils.get_document_type` module."""

import pytest

from mirascope.core.base._utils._get_document_type import get_document_type

PDF_DATA = b"%PDF-1.0\ntrailer<</Root<</Pages<</Kids[]>>>>>>%%EOF"


def test_get_document_type() -> None:
    """Test the get_image_type function."""
    assert get_document_type(PDF_DATA) == "pdf"
    with pytest.raises(ValueError, match="Unsupported document type"):
        get_document_type(b"invalid")
