"""Tests for Document content class."""

import base64
import tempfile
from pathlib import Path

import pytest

from mirascope.llm.content.document import (
    Base64DocumentSource,
    Document,
    TextDocumentSource,
    URLDocumentSource,
    infer_document_type,
    mime_type_from_extension,
)

# PDF magic bytes: %PDF
PDF_MAGIC_BYTES = b"%PDF-1.4"


class TestInferDocumentType:
    """Tests for infer_document_type function."""

    def test_detects_pdf_from_magic_bytes(self) -> None:
        assert infer_document_type(PDF_MAGIC_BYTES) == "application/pdf"

    def test_returns_none_for_unknown_bytes(self) -> None:
        unknown = b"\x00\x01\x02\x03"
        assert infer_document_type(unknown) is None

    def test_returns_none_for_data_shorter_than_4_bytes(self) -> None:
        short = b"%P"
        assert infer_document_type(short) is None


class TestMimeTypeFromExtension:
    """Tests for mime_type_from_extension function."""

    @pytest.mark.parametrize(
        "ext,expected",
        [
            (".pdf", "application/pdf"),
            (".txt", "text/plain"),
            (".json", "application/json"),
            (".js", "text/javascript"),
            (".mjs", "text/javascript"),
            (".py", "text/x-python"),
            (".html", "text/html"),
            (".htm", "text/html"),
            (".css", "text/css"),
            (".xml", "text/xml"),
            (".rtf", "text/rtf"),
        ],
    )
    def test_maps_extension_to_mime_type(self, ext: str, expected: str) -> None:
        assert mime_type_from_extension(ext) == expected

    def test_is_case_insensitive(self) -> None:
        assert mime_type_from_extension(".PDF") == "application/pdf"

    def test_throws_for_unsupported_extension(self) -> None:
        with pytest.raises(
            ValueError, match="Unsupported document file extension: .docx"
        ):
            mime_type_from_extension(".docx")


class TestDocumentFromUrl:
    """Tests for Document.from_url class method."""

    def test_creates_url_document_source(self) -> None:
        doc = Document.from_url("https://example.com/doc.pdf")
        assert isinstance(doc.source, URLDocumentSource)
        assert doc.source.type == "url_document_source"
        assert doc.source.url == "https://example.com/doc.pdf"
        assert doc.type == "document"

    def test_accepts_download_option(self) -> None:
        doc = Document.from_url("https://example.com/doc.pdf", download=True)
        assert isinstance(doc.source, URLDocumentSource)


class TestDocumentFromBytes:
    """Tests for Document.from_bytes class method."""

    def test_creates_base64_document_source_for_pdf_bytes(self) -> None:
        doc = Document.from_bytes(PDF_MAGIC_BYTES)
        assert doc.type == "document"
        assert isinstance(doc.source, Base64DocumentSource)
        assert doc.source.type == "base64_document_source"
        assert doc.source.media_type == "application/pdf"
        assert doc.source.data == base64.b64encode(PDF_MAGIC_BYTES).decode("utf-8")

    def test_creates_text_document_source_with_explicit_text_mime_type(self) -> None:
        text = b"Hello, world!"
        doc = Document.from_bytes(text, mime_type="text/plain")
        assert doc.type == "document"
        assert isinstance(doc.source, TextDocumentSource)
        assert doc.source.type == "text_document_source"
        assert doc.source.data == "Hello, world!"
        assert doc.source.media_type == "text/plain"

    def test_creates_base64_document_source_with_explicit_pdf_mime_type(self) -> None:
        data = b"\x00\x01\x02"
        doc = Document.from_bytes(data, mime_type="application/pdf")
        assert isinstance(doc.source, Base64DocumentSource)

    def test_throws_for_unknown_bytes_without_mime_type(self) -> None:
        unknown = b"\x00\x01\x02\x03"
        with pytest.raises(ValueError, match="Cannot infer document type from bytes"):
            Document.from_bytes(unknown)


class TestDocumentFromFile:
    """Tests for Document.from_file class method."""

    def test_creates_base64_document_source_for_pdf_file(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(PDF_MAGIC_BYTES)
            temp_path = f.name

        try:
            doc = Document.from_file(temp_path)
            assert doc.type == "document"
            assert isinstance(doc.source, Base64DocumentSource)
            assert doc.source.type == "base64_document_source"
            assert doc.source.media_type == "application/pdf"
        finally:
            Path(temp_path).unlink()

    def test_creates_text_document_source_for_txt_file(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("Hello, text!")
            temp_path = f.name

        try:
            doc = Document.from_file(temp_path)
            assert doc.type == "document"
            assert isinstance(doc.source, TextDocumentSource)
            assert doc.source.type == "text_document_source"
            assert doc.source.data == "Hello, text!"
            assert doc.source.media_type == "text/plain"
        finally:
            Path(temp_path).unlink()

    def test_creates_text_document_source_for_json_file(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            f.write('{"key": "value"}')
            temp_path = f.name

        try:
            doc = Document.from_file(temp_path)
            assert isinstance(doc.source, TextDocumentSource)
            assert doc.source.media_type == "application/json"
        finally:
            Path(temp_path).unlink()

    def test_uses_explicit_mime_type_override(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            f.write(PDF_MAGIC_BYTES)
            temp_path = f.name

        try:
            doc = Document.from_file(temp_path, mime_type="application/pdf")
            assert isinstance(doc.source, Base64DocumentSource)
            assert doc.source.media_type == "application/pdf"
        finally:
            Path(temp_path).unlink()

    def test_throws_for_unsupported_file_extension(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            f.write(b"test")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Unsupported document file extension"):
                Document.from_file(temp_path)
        finally:
            Path(temp_path).unlink()
