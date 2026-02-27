"""End-to-end tests for resuming structured output across formatting modes."""

import pytest

from mirascope import llm
from tests.e2e.conftest import FORMATTING_MODES, STRUCTURED_OUTPUT_MODEL_IDS
from tests.utils import Snapshot, snapshot_test


@pytest.mark.parametrize("model_id", STRUCTURED_OUTPUT_MODEL_IDS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
def test_structured_output_resume(
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
    snapshot: Snapshot,
) -> None:
    """Test resume on a structured output response across all formatting modes."""
    format = (
        llm.format(int, mode=formatting_mode) if formatting_mode is not None else int
    )

    @llm.call(model_id, format=format)
    def lucky_number() -> str:
        return "Choose a lucky number between 1 and 10"

    with snapshot_test(snapshot) as snap:
        response = lucky_number()
        num = response.parse()
        assert isinstance(num, int)

        response = response.resume("Ok, now choose a different lucky number")
        num2 = response.parse()
        assert isinstance(num2, int)

        snap.set_response(response)


@pytest.mark.parametrize("model_id", STRUCTURED_OUTPUT_MODEL_IDS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
def test_structured_output_resume_stream(
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
    snapshot: Snapshot,
) -> None:
    """Test resume on a streamed structured output response across all formatting modes."""
    format = (
        llm.format(int, mode=formatting_mode) if formatting_mode is not None else int
    )

    @llm.call(model_id, format=format)
    def lucky_number() -> str:
        return "Choose a lucky number between 1 and 10"

    with snapshot_test(snapshot) as snap:
        stream_response = lucky_number.stream()
        stream_response.finish()
        num = stream_response.parse()
        assert isinstance(num, int)

        stream_response = stream_response.resume(
            "Ok, now choose a different lucky number"
        )
        stream_response.finish()
        num2 = stream_response.parse()
        assert isinstance(num2, int)

        snap.set_response(stream_response)


@pytest.mark.parametrize("model_id", STRUCTURED_OUTPUT_MODEL_IDS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
def test_structured_output_resume_cross_model(
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
    snapshot: Snapshot,
) -> None:
    """Test resume on a structured output with a different model."""
    format = (
        llm.format(int, mode=formatting_mode) if formatting_mode is not None else int
    )

    # Use a different provider for the initial call
    initial_model: llm.ModelId = (
        "anthropic/claude-sonnet-4-0"
        if model_id.startswith("google/")
        else "google/gemini-2.5-flash"
    )

    @llm.call(initial_model, format=format)
    def lucky_number() -> str:
        return "Choose a lucky number between 1 and 10"

    with snapshot_test(snapshot) as snap:
        response = lucky_number()
        num = response.parse()
        assert isinstance(num, int)

        with llm.model(model_id):
            response = response.resume("Ok, now choose a different lucky number")
        num2 = response.parse()
        assert isinstance(num2, int)

        snap.set_response(response)
