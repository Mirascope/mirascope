"""End-to-end tests for a LLM call with an image input."""

from pathlib import Path

import pytest

from mirascope import llm
from mirascope.llm.content.image import MIME_TYPES, ImageMimeType
from tests.e2e.conftest import E2E_MODEL_IDS
from tests.utils import (
    Snapshot,
    snapshot_test,
)

ASSETS_DIR = Path(__file__).parent.parent / "assets" / "images"

IMAGE_PATHS: dict[ImageMimeType, str] = {
    "image/png": str(ASSETS_DIR / "test.png"),
    "image/jpeg": str(ASSETS_DIR / "test.jpg"),
    "image/webp": str(ASSETS_DIR / "test.webp"),
    "image/gif": str(ASSETS_DIR / "test.gif"),
    "image/heic": str(ASSETS_DIR / "test.heic"),
    "image/heif": str(ASSETS_DIR / "test.heif"),
}

IMAGE_URLS: dict[ImageMimeType, str] = {
    "image/png": "https://en.wikipedia.org/static/images/icons/wikipedia.png",
    "image/jpeg": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Example.jpg",
    "image/webp": "https://www.gstatic.com/webp/gallery/1.webp",
    "image/gif": "https://upload.wikimedia.org/wikipedia/commons/2/2c/Rotating_earth_%28large%29.gif",
    "image/heic": "https://raw.githubusercontent.com/strukturag/libheif/master/examples/example.heic",
    "image/heif": "https://raw.githubusercontent.com/strukturag/libheif/master/examples/example.heic",
}

UNSUPPORTED_CONTENT: dict[str, set[ImageMimeType]] = {
    "google/": {"image/gif"},
    "openai/": {"image/heic", "image/heif"},
    "anthropic": {"image/heic", "image/heif"},
}

UNSUPPORTED_URL: dict[str, set[ImageMimeType]] = {
    "google/": {"image/gif"},
    "openai/": {"image/png", "image/jpeg", "image/webp", "image/gif", "image/heic", "image/heif"},
    "anthropic": {"image/heic", "image/heif"},
}


def _mime_id(mime_type: ImageMimeType) -> str:
    return mime_type.split("/")[1]


def _should_skip(
    model_id: llm.ModelId,
    mime_type: ImageMimeType,
    unsupported: dict[str, set[ImageMimeType]],
) -> str | None:
    for prefix, types in unsupported.items():
        if model_id.startswith(prefix) and mime_type in types:
            return f"{model_id} does not support {mime_type}"
    return None


@pytest.mark.parametrize("mime_type", MIME_TYPES, ids=_mime_id)
@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_call_with_image_content(
    model_id: llm.ModelId,
    mime_type: ImageMimeType,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test a call using an image loaded from file for each supported MIME type."""
    reason = _should_skip(model_id, mime_type, UNSUPPORTED_CONTENT)
    if reason:
        pytest.skip(reason)

    image_path = IMAGE_PATHS[mime_type]
    if not Path(image_path).exists():
        pytest.skip(f"Asset not found: {image_path}")

    @llm.call(model_id)
    def analyze_image(image_path: str) -> llm.UserContent:
        return [
            "Describe the following image in one sentence",
            llm.Image.from_file(image_path),
        ]

    with snapshot_test(snapshot, caplog) as snap:
        response = analyze_image(image_path)
        snap.set_response(response)


@pytest.mark.parametrize("mime_type", MIME_TYPES, ids=_mime_id)
@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_call_with_image_url(
    model_id: llm.ModelId,
    mime_type: ImageMimeType,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test a call using an image referenced by URL for each supported MIME type."""
    reason = _should_skip(model_id, mime_type, UNSUPPORTED_URL)
    if reason:
        pytest.skip(reason)

    image_url = IMAGE_URLS[mime_type]

    @llm.call(model_id)
    def analyze_image(image_url: str) -> llm.UserContent:
        return [
            "Describe the following image in one sentence",
            llm.Image.from_url(image_url),
        ]

    with snapshot_test(snapshot, caplog) as snap:
        response = analyze_image(image_url)
        snap.set_response(response)
