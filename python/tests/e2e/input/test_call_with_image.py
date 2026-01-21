"""End-to-end tests for a LLM call with an image input."""

from pathlib import Path

import pytest

from mirascope import llm
from tests.e2e.conftest import E2E_MODEL_IDS
from tests.utils import (
    Snapshot,
    snapshot_test,
)

WIKIPEDIA_ICON_URL = "https://en.wikipedia.org/static/images/icons/wikipedia.png"
WIKIPEDIA_ICON_PATH = str(
    Path(__file__).parent.parent / "assets" / "images" / "wikipedia.png"
)


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_call_with_image_content(
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test a call using an image loaded from file."""

    @llm.call(model_id)
    def analyze_image(image_path: str) -> llm.UserContent:
        return [
            "Describe the following image in one sentence",
            llm.Image.from_file(image_path),
        ]

    with snapshot_test(snapshot, caplog) as snap:
        response = analyze_image(WIKIPEDIA_ICON_PATH)
        snap.set_response(response)


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_call_with_image_url(
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test a call using an image referenced by url."""

    @llm.call(model_id)
    def analyze_image(image_url: str) -> llm.UserContent:
        return [
            "Describe the following image in one sentence",
            llm.Image.from_url(image_url),
        ]

    with snapshot_test(snapshot, caplog) as snap:
        response = analyze_image(WIKIPEDIA_ICON_URL)
        snap.set_response(response)
