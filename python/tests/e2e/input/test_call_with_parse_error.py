"""End-to-end tests for a LLM call with parse error recovery."""

import pytest

from mirascope import llm
from tests.e2e.conftest import E2E_MODEL_IDS
from tests.utils import (
    Snapshot,
    snapshot_test,
)


@llm.output_parser(
    formatting_instructions="Respond with a single word: the passphrase."
)
def extract_passphrase(response: llm.AnyResponse) -> str:
    """Extract a passphrase from the response."""
    text = response.text().strip().lower()
    if text != "cake":
        raise ValueError("Incorrect passphrase. The correct passphrase is 'cake'")
    return "the cake is a lie"


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_call_with_parse_error(
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that ParseError recovery works with retry_message."""

    @llm.call(model_id, format=extract_passphrase)
    def get_passphrase() -> str:
        return "Find out the secret and report back."

    max_retries = 3

    with snapshot_test(snapshot, caplog) as snap:
        response = get_passphrase()

        for attempt in range(max_retries):
            try:
                response.parse()
                break
            except llm.ParseError as e:
                if attempt == max_retries - 1:
                    raise
                response = response.resume(e.retry_message())

        snap.set_response(response)
