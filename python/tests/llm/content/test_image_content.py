"""Tests for Image content class."""

import tempfile
from pathlib import Path

import httpx
import pytest
from pytest_httpserver import HTTPServer

from mirascope.llm.content.image import (
    MAX_IMAGE_SIZE,
    Base64ImageSource,
    Image,
    URLImageSource,
)


@pytest.fixture
def image_data() -> dict[str, bytes]:
    """Provide sample image data for different formats (minimum 12 bytes each)."""
    return {
        "png": b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR",
        "jpeg": b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01",
        "webp": b"RIFF\x00\x00\x00\x00WEBP",
        "gif87a": b"GIF87a\x00\x00\x00\x00\x00\x00",
        "gif89a": b"GIF89a\x00\x00\x00\x00\x00\x00",
        "heic_ftypheic": b"\x00\x00\x00\x18ftypheic",
        "heic_ftypheix": b"\x00\x00\x00\x18ftypheix",
        "heif_ftypmif1": b"\x00\x00\x00\x18ftypmif1",
        "heif_ftypmsf1": b"\x00\x00\x00\x18ftypmsf1",
        "heif_ftyphevc": b"\x00\x00\x00\x18ftyphevc",
        "heif_ftyphevx": b"\x00\x00\x00\x18ftyphevx",
        "unsupported": b"random unsupported data",
    }


IMAGE_FORMAT_TESTS = [
    ("png", "image/png"),
    ("jpeg", "image/jpeg"),
    ("webp", "image/webp"),
    ("gif87a", "image/gif"),
    ("gif89a", "image/gif"),
    ("heic_ftypheic", "image/heic"),
    ("heic_ftypheix", "image/heic"),
    ("heif_ftypmif1", "image/heif"),
    ("heif_ftypmsf1", "image/heif"),
    ("heif_ftyphevc", "image/heif"),
    ("heif_ftyphevx", "image/heif"),
]


class TestImageFromUrl:
    """Tests for Image.from_url class method."""

    def test_from_url_creates_url_reference(self) -> None:
        """Test creating an Image reference from URL without downloading."""
        url = "https://example.com/image.png"
        image = Image.from_url(url)

        assert isinstance(image.source, URLImageSource)
        assert image.source.url == url
        assert image.source.type == "url_image_source"


class TestImageDownload:
    """Tests for Image.download class method."""

    @pytest.mark.parametrize("format_name,expected_mime", IMAGE_FORMAT_TESTS)
    def test_download_detects_mime_type_from_magic_bytes(
        self,
        httpserver: HTTPServer,
        image_data: dict[str, bytes],
        format_name: str,
        expected_mime: str,
    ) -> None:
        """Test that download() detects MIME type from magic bytes."""
        httpserver.expect_request("/image").respond_with_data(image_data[format_name])
        url = httpserver.url_for("/image")

        image = Image.download(url)

        assert isinstance(image.source, Base64ImageSource)
        assert image.source.type == "base64_image_source"
        assert image.source.mime_type == expected_mime
        assert len(image.source.data) > 0

    def test_download_follows_redirects(
        self, httpserver: HTTPServer, image_data: dict[str, bytes]
    ) -> None:
        """Test that download follows redirects."""
        httpserver.expect_request("/redirect").respond_with_data(
            "", status=302, headers={"Location": "/image"}
        )
        httpserver.expect_request("/image").respond_with_data(image_data["png"])
        url = httpserver.url_for("/redirect")

        image = Image.download(url)

        assert isinstance(image.source, Base64ImageSource)
        assert image.source.mime_type == "image/png"

    def test_download_raises_on_unsupported_format(
        self, httpserver: HTTPServer, image_data: dict[str, bytes]
    ) -> None:
        """Test that download raises ValueError for unsupported image format."""
        httpserver.expect_request("/image").respond_with_data(image_data["unsupported"])
        url = httpserver.url_for("/image")

        with pytest.raises(ValueError, match="Unsupported image type"):
            Image.download(url)

    def test_download_raises_on_http_error(self, httpserver: HTTPServer) -> None:
        """Test that download raises on HTTP errors."""
        httpserver.expect_request("/image").respond_with_data("", status=404)
        url = httpserver.url_for("/image")

        with pytest.raises(httpx.HTTPStatusError):
            Image.download(url)

    def test_download_enforces_size_limit(self, httpserver: HTTPServer) -> None:
        """Test that download enforces the size limit."""
        large_data = b"\xff\xd8\xff" + b"x" * (MAX_IMAGE_SIZE + 1)
        httpserver.expect_request("/image").respond_with_data(large_data)
        url = httpserver.url_for("/image")

        with pytest.raises(ValueError, match="exceeds maximum allowed size"):
            Image.download(url)

    def test_download_respects_custom_size_limit(
        self, httpserver: HTTPServer, image_data: dict[str, bytes]
    ) -> None:
        """Test that download respects custom max_size parameter."""
        httpserver.expect_request("/image").respond_with_data(image_data["png"])
        url = httpserver.url_for("/image")

        with pytest.raises(ValueError, match="exceeds maximum allowed size"):
            Image.download(url, max_size=10)


class TestImageDownloadAsync:
    """Tests for Image.download_async class method."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "format_name,expected_mime",
        [
            ("png", "image/png"),
            ("jpeg", "image/jpeg"),
            ("webp", "image/webp"),
            ("gif89a", "image/gif"),
        ],
    )
    async def test_download_async_detects_mime_type(
        self,
        httpserver: HTTPServer,
        image_data: dict[str, bytes],
        format_name: str,
        expected_mime: str,
    ) -> None:
        """Test that download_async() detects MIME type from magic bytes."""
        httpserver.expect_request("/image").respond_with_data(image_data[format_name])
        url = httpserver.url_for("/image")

        image = await Image.download_async(url)

        assert isinstance(image.source, Base64ImageSource)
        assert image.source.mime_type == expected_mime

    @pytest.mark.asyncio
    async def test_download_async_enforces_size_limit(
        self, httpserver: HTTPServer
    ) -> None:
        """Test that download_async enforces the size limit."""
        large_data = b"\xff\xd8\xff" + b"x" * (MAX_IMAGE_SIZE + 1)
        httpserver.expect_request("/image").respond_with_data(large_data)
        url = httpserver.url_for("/image")

        with pytest.raises(ValueError, match="exceeds maximum allowed size"):
            await Image.download_async(url)

    @pytest.mark.asyncio
    async def test_download_async_raises_on_unsupported_format(
        self, httpserver: HTTPServer, image_data: dict[str, bytes]
    ) -> None:
        """Test that download_async raises ValueError for unsupported format."""
        httpserver.expect_request("/image").respond_with_data(image_data["unsupported"])
        url = httpserver.url_for("/image")

        with pytest.raises(ValueError, match="Unsupported image type"):
            await Image.download_async(url)


class TestImageFromFile:
    """Tests for Image.from_file class method."""

    @pytest.mark.parametrize("data_key,expected_mime", IMAGE_FORMAT_TESTS)
    def test_from_file_detects_mime_type(
        self, image_data: dict[str, bytes], data_key: str, expected_mime: str
    ) -> None:
        """Test that from_file detects MIME type from magic bytes (not extension)."""
        with tempfile.NamedTemporaryFile(suffix=".unknown", delete=False) as f:
            f.write(image_data[data_key])
            temp_path = f.name

        try:
            image = Image.from_file(temp_path)

            assert isinstance(image.source, Base64ImageSource)
            assert image.source.mime_type == expected_mime
        finally:
            Path(temp_path).unlink()

    def test_from_file_raises_on_unsupported_format(
        self, image_data: dict[str, bytes]
    ) -> None:
        """Test that from_file raises ValueError for unsupported format."""
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as f:
            f.write(image_data["unsupported"])
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Unsupported image type"):
                Image.from_file(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_from_file_not_found(self) -> None:
        """Test FileNotFoundError is raised for non-existent file."""
        with pytest.raises(FileNotFoundError):
            Image.from_file("/nonexistent/path/to/file.png")

    def test_from_file_enforces_size_limit(self, image_data: dict[str, bytes]) -> None:
        """Test that from_file enforces the size limit."""
        large_data = b"\xff\xd8\xff" + b"x" * (MAX_IMAGE_SIZE + 1)
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(large_data)
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="exceeds maximum allowed size"):
                Image.from_file(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_from_file_respects_custom_size_limit(
        self, image_data: dict[str, bytes]
    ) -> None:
        """Test that from_file respects custom max_size parameter."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(image_data["png"])
            temp_path = f.name

        try:
            # Should fail with a very small limit
            with pytest.raises(ValueError, match="exceeds maximum allowed size"):
                Image.from_file(temp_path, max_size=10)
        finally:
            Path(temp_path).unlink()


class TestImageFromBytes:
    """Tests for Image.from_bytes class method."""

    @pytest.mark.parametrize("data_key,expected_mime", IMAGE_FORMAT_TESTS)
    def test_from_bytes_detects_mime_type(
        self, image_data: dict[str, bytes], data_key: str, expected_mime: str
    ) -> None:
        """Test that from_bytes detects MIME type from magic bytes."""
        image = Image.from_bytes(image_data[data_key])

        assert isinstance(image.source, Base64ImageSource)
        assert image.source.mime_type == expected_mime

    def test_from_bytes_raises_on_unsupported_format(
        self, image_data: dict[str, bytes]
    ) -> None:
        """Test that from_bytes raises ValueError for unsupported format."""
        with pytest.raises(ValueError, match="Unsupported image type"):
            Image.from_bytes(image_data["unsupported"])

    def test_from_bytes_raises_on_data_too_small(self) -> None:
        """Test that from_bytes raises ValueError for data that's too small."""
        with pytest.raises(ValueError, match="Image data too small to determine type"):
            Image.from_bytes(b"short")

    def test_from_bytes_enforces_size_limit(self) -> None:
        """Test that from_bytes enforces the size limit."""
        large_data = b"\xff\xd8\xff" + b"x" * (MAX_IMAGE_SIZE + 1)

        with pytest.raises(ValueError, match="exceeds maximum allowed size"):
            Image.from_bytes(large_data)

    def test_from_bytes_respects_custom_size_limit(
        self, image_data: dict[str, bytes]
    ) -> None:
        """Test that from_bytes respects custom max_size parameter."""
        with pytest.raises(ValueError, match="exceeds maximum allowed size"):
            Image.from_bytes(image_data["png"], max_size=10)
