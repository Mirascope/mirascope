"""End-to-end tests for a LLM call with a document input."""

from pathlib import Path

import pytest

from mirascope import llm
from tests.e2e.conftest import E2E_MODEL_IDS
from tests.utils import (
    Snapshot,
    snapshot_test,
)

TEST_PDF_PATH = str(Path(__file__).parent.parent / "assets" / "documents" / "test.pdf")

TEST_PDF_URL = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

# Document tests use non-reasoning models to avoid consuming all tokens in reasoning
DOCUMENT_MODEL_IDS: list[llm.ModelId] = [
    model_id
    for model_id in E2E_MODEL_IDS
    if "beta" not in model_id and "mlx" not in model_id
]

# URL documents are only supported by Anthropic and OpenAI Responses
# Google and OpenAI Completions don't support URL-referenced documents
URL_DOCUMENT_MODEL_IDS: list[llm.ModelId] = [
    model_id
    for model_id in DOCUMENT_MODEL_IDS
    if "google/" not in model_id and ":completions" not in model_id
]


@pytest.mark.parametrize("model_id", DOCUMENT_MODEL_IDS)
@pytest.mark.vcr
def test_call_with_document_content(
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test a call using a document loaded from file."""

    @llm.call(model_id)
    def analyze_document(doc_path: str) -> llm.UserContent:
        return [
            "What text is in this PDF document? Reply in one short sentence.",
            llm.Document.from_file(doc_path),
        ]

    with snapshot_test(snapshot, caplog) as snap:
        response = analyze_document(TEST_PDF_PATH)
        snap.set_response(response)


@pytest.mark.parametrize("model_id", URL_DOCUMENT_MODEL_IDS)
@pytest.mark.vcr
def test_call_with_document_url(
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test a call using a document referenced by URL."""

    @llm.call(model_id)
    def analyze_document(doc_url: str) -> llm.UserContent:
        return [
            "What is this PDF about? Reply in one short sentence.",
            llm.Document.from_url(doc_url),
        ]

    with snapshot_test(snapshot, caplog) as snap:
        response = analyze_document(TEST_PDF_URL)
        snap.set_response(response)
