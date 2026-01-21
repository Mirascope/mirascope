"""Tests for Audio content class."""

import tempfile
from pathlib import Path

import httpx
import pytest
from pytest_httpserver import HTTPServer

from mirascope.llm.content.audio import MAX_AUDIO_SIZE, Audio, Base64AudioSource


@pytest.fixture
def audio_data() -> dict[str, bytes]:
    """Provide sample audio data for different formats (minimum 12 bytes each)."""
    return {
        "wav": b"RIFF\x00\x00\x00\x00WAVE",
        "mp3_id3": b"ID3\x03\x00\x00\x00\x00\x00\x00\x00\x00",
        "mp3_frame": b"\xff\xfb\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        "aiff": b"FORM\x00\x00\x00\x00AIFF",
        "aac_f1": b"\xff\xf1\x50\x80\x00\x00\x00\x00\x00\x00\x00\x00",
        "aac_f9": b"\xff\xf9\x50\x80\x00\x00\x00\x00\x00\x00\x00\x00",
        "ogg": b"OggS\x00\x02\x00\x00\x00\x00\x00\x00",
        "flac": b"fLaC\x00\x00\x00\x22\x00\x00\x00\x00",
        "unsupported": b"random unsupported data",
    }


AUDIO_FORMAT_TESTS = [
    ("wav", "audio/wav"),
    ("mp3_id3", "audio/mp3"),
    ("mp3_frame", "audio/mp3"),
    ("aiff", "audio/aiff"),
    ("aac_f1", "audio/aac"),
    ("aac_f9", "audio/aac"),
    ("ogg", "audio/ogg"),
    ("flac", "audio/flac"),
]


class TestAudioDownload:
    """Tests for Audio.download class method."""

    @pytest.mark.parametrize("format_name,expected_mime", AUDIO_FORMAT_TESTS)
    def test_download_detects_mime_type_from_magic_bytes(
        self,
        httpserver: HTTPServer,
        audio_data: dict[str, bytes],
        format_name: str,
        expected_mime: str,
    ) -> None:
        """Test that download() detects MIME type from magic bytes."""
        httpserver.expect_request("/audio").respond_with_data(audio_data[format_name])
        url = httpserver.url_for("/audio")

        audio = Audio.download(url)

        assert isinstance(audio.source, Base64AudioSource)
        assert audio.source.type == "base64_audio_source"
        assert audio.source.mime_type == expected_mime
        assert len(audio.source.data) > 0

    def test_download_follows_redirects(
        self, httpserver: HTTPServer, audio_data: dict[str, bytes]
    ) -> None:
        """Test that download follows redirects."""
        httpserver.expect_request("/redirect").respond_with_data(
            "", status=302, headers={"Location": "/audio"}
        )
        httpserver.expect_request("/audio").respond_with_data(audio_data["wav"])
        url = httpserver.url_for("/redirect")

        audio = Audio.download(url)

        assert isinstance(audio.source, Base64AudioSource)
        assert audio.source.mime_type == "audio/wav"

    def test_download_raises_on_unsupported_format(
        self, httpserver: HTTPServer, audio_data: dict[str, bytes]
    ) -> None:
        """Test that download raises ValueError for unsupported audio format."""
        httpserver.expect_request("/audio").respond_with_data(audio_data["unsupported"])
        url = httpserver.url_for("/audio")

        with pytest.raises(ValueError, match="Unsupported audio type"):
            Audio.download(url)

    def test_download_raises_on_http_error(self, httpserver: HTTPServer) -> None:
        """Test that download raises on HTTP errors."""
        httpserver.expect_request("/audio").respond_with_data("", status=404)
        url = httpserver.url_for("/audio")

        with pytest.raises(httpx.HTTPStatusError):
            Audio.download(url)

    def test_download_enforces_size_limit(self, httpserver: HTTPServer) -> None:
        """Test that download enforces the size limit."""
        large_data = b"RIFF\x00\x00\x00\x00WAVE" + b"x" * (MAX_AUDIO_SIZE + 1)
        httpserver.expect_request("/audio").respond_with_data(large_data)
        url = httpserver.url_for("/audio")

        with pytest.raises(ValueError, match="exceeds maximum allowed size"):
            Audio.download(url)

    def test_download_respects_custom_size_limit(
        self, httpserver: HTTPServer, audio_data: dict[str, bytes]
    ) -> None:
        """Test that download respects custom max_size parameter."""
        httpserver.expect_request("/audio").respond_with_data(audio_data["wav"])
        url = httpserver.url_for("/audio")

        with pytest.raises(ValueError, match="exceeds maximum allowed size"):
            Audio.download(url, max_size=10)


class TestAudioDownloadAsync:
    """Tests for Audio.download_async class method."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "format_name,expected_mime",
        [
            ("wav", "audio/wav"),
            ("mp3_id3", "audio/mp3"),
            ("aiff", "audio/aiff"),
            ("ogg", "audio/ogg"),
        ],
    )
    async def test_download_async_detects_mime_type(
        self,
        httpserver: HTTPServer,
        audio_data: dict[str, bytes],
        format_name: str,
        expected_mime: str,
    ) -> None:
        """Test that download_async() detects MIME type from magic bytes."""
        httpserver.expect_request("/audio").respond_with_data(audio_data[format_name])
        url = httpserver.url_for("/audio")

        audio = await Audio.download_async(url)

        assert isinstance(audio.source, Base64AudioSource)
        assert audio.source.mime_type == expected_mime

    @pytest.mark.asyncio
    async def test_download_async_enforces_size_limit(
        self, httpserver: HTTPServer
    ) -> None:
        """Test that download_async enforces the size limit."""
        large_data = b"RIFF\x00\x00\x00\x00WAVE" + b"x" * (MAX_AUDIO_SIZE + 1)
        httpserver.expect_request("/audio").respond_with_data(large_data)
        url = httpserver.url_for("/audio")

        with pytest.raises(ValueError, match="exceeds maximum allowed size"):
            await Audio.download_async(url)

    @pytest.mark.asyncio
    async def test_download_async_raises_on_unsupported_format(
        self, httpserver: HTTPServer, audio_data: dict[str, bytes]
    ) -> None:
        """Test that download_async raises ValueError for unsupported format."""
        httpserver.expect_request("/audio").respond_with_data(audio_data["unsupported"])
        url = httpserver.url_for("/audio")

        with pytest.raises(ValueError, match="Unsupported audio type"):
            await Audio.download_async(url)


class TestAudioFromFile:
    """Tests for Audio.from_file class method."""

    @pytest.mark.parametrize("data_key,expected_mime", AUDIO_FORMAT_TESTS)
    def test_from_file_detects_mime_type(
        self, audio_data: dict[str, bytes], data_key: str, expected_mime: str
    ) -> None:
        """Test that from_file detects MIME type from magic bytes (not extension)."""
        with tempfile.NamedTemporaryFile(suffix=".unknown", delete=False) as f:
            f.write(audio_data[data_key])
            temp_path = f.name

        try:
            audio = Audio.from_file(temp_path)

            assert isinstance(audio.source, Base64AudioSource)
            assert audio.source.mime_type == expected_mime
        finally:
            Path(temp_path).unlink()

    def test_from_file_raises_on_unsupported_format(
        self, audio_data: dict[str, bytes]
    ) -> None:
        """Test that from_file raises ValueError for unsupported format."""
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as f:
            f.write(audio_data["unsupported"])
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Unsupported audio type"):
                Audio.from_file(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_from_file_not_found(self) -> None:
        """Test FileNotFoundError is raised for non-existent file."""
        with pytest.raises(FileNotFoundError):
            Audio.from_file("/nonexistent/path/to/file.mp3")

    def test_from_file_enforces_size_limit(self, audio_data: dict[str, bytes]) -> None:
        """Test that from_file enforces the size limit."""
        large_data = b"RIFF\x00\x00\x00\x00WAVE" + b"x" * (MAX_AUDIO_SIZE + 1)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(large_data)
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="exceeds maximum allowed size"):
                Audio.from_file(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_from_file_respects_custom_size_limit(
        self, audio_data: dict[str, bytes]
    ) -> None:
        """Test that from_file respects custom max_size parameter."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_data["wav"])
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="exceeds maximum allowed size"):
                Audio.from_file(temp_path, max_size=10)
        finally:
            Path(temp_path).unlink()


class TestAudioFromBytes:
    """Tests for Audio.from_bytes class method."""

    @pytest.mark.parametrize("data_key,expected_mime", AUDIO_FORMAT_TESTS)
    def test_from_bytes_detects_mime_type(
        self, audio_data: dict[str, bytes], data_key: str, expected_mime: str
    ) -> None:
        """Test that from_bytes detects MIME type from magic bytes."""
        audio = Audio.from_bytes(audio_data[data_key])

        assert isinstance(audio.source, Base64AudioSource)
        assert audio.source.mime_type == expected_mime

    def test_from_bytes_raises_on_unsupported_format(
        self, audio_data: dict[str, bytes]
    ) -> None:
        """Test that from_bytes raises ValueError for unsupported format."""
        with pytest.raises(ValueError, match="Unsupported audio type"):
            Audio.from_bytes(audio_data["unsupported"])

    def test_from_bytes_raises_on_data_too_small(self) -> None:
        """Test that from_bytes raises ValueError for data that's too small."""
        with pytest.raises(ValueError, match="Audio data too small to determine type"):
            Audio.from_bytes(b"short")

    def test_from_bytes_enforces_size_limit(self) -> None:
        """Test that from_bytes enforces the size limit."""
        large_data = b"RIFF\x00\x00\x00\x00WAVE" + b"x" * (MAX_AUDIO_SIZE + 1)

        with pytest.raises(ValueError, match="exceeds maximum allowed size"):
            Audio.from_bytes(large_data)

    def test_from_bytes_respects_custom_size_limit(
        self, audio_data: dict[str, bytes]
    ) -> None:
        """Test that from_bytes respects custom max_size parameter."""
        with pytest.raises(ValueError, match="exceeds maximum allowed size"):
            Audio.from_bytes(audio_data["wav"], max_size=10)
