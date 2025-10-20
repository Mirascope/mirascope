"""End-to-end tests for a LLM call with an image input."""

import pytest

from mirascope import llm
from tests.e2e.conftest import PROVIDER_MODEL_ID_PAIRS
from tests.utils import (
    Snapshot,
    snapshot_test,
)

WIKIPEDIA_ICON_URL = "https://en.wikipedia.org/static/images/icons/wikipedia.png"


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_call_with_image_content(
    provider: llm.Provider,
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test a call using a downloaded image."""

    @llm.call(provider=provider, model_id=model_id)
    def analyze_image(image_url: str) -> llm.UserContent:
        return [
            "Describe the following image",
            llm.Image.download(image_url),
        ]

    with snapshot_test(snapshot, caplog) as snap:
        response = analyze_image(WIKIPEDIA_ICON_URL)
        snap.set_response(response)


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_call_with_image_url(
    provider: llm.Provider,
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test a call using an image referenced by url."""

    @llm.call(provider=provider, model_id=model_id)
    def analyze_image(image_url: str) -> llm.UserContent:
        return [
            "Describe the following image",
            llm.Image.from_url(image_url),
        ]

    with snapshot_test(snapshot, caplog) as snap:
        response = analyze_image(WIKIPEDIA_ICON_URL)
        snap.set_response(response)
