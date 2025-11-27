"""End-to-end tests for a LLM call with audio input."""

from pathlib import Path

import pytest

from mirascope import llm
from tests.e2e.conftest import E2E_MODEL_IDS
from tests.utils import (
    Snapshot,
    snapshot_test,
)

HELLO_AUDIO_PATH = str(
    Path(__file__).parent.parent / "assets" / "audio" / "tagline.mp3"
)

E2E_MODEL_IDS = [*E2E_MODEL_IDS, "openai/gpt-audio"]


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_call_with_audio(
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test a call using an audio file loaded from disk."""

    @llm.call(model_id)
    def transcribe_audio(audio_path: str) -> llm.UserContent:
        return [
            "Repeat exactly what you hear:",
            llm.Audio.from_file(audio_path),
        ]

    with snapshot_test(snapshot, caplog) as snap:
        response = transcribe_audio(HELLO_AUDIO_PATH)
        snap.set_response(response)
