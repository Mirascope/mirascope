"""End-to-end tests for a LLM call with audio input."""

from pathlib import Path

import pytest

from mirascope import llm
from tests.e2e.conftest import PROVIDER_MODEL_ID_PAIRS
from tests.utils import (
    Snapshot,
    snapshot_test,
)

HELLO_AUDIO_PATH = str(
    Path(__file__).parent.parent / "assets" / "audio" / "tagline.mp3"
)


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_call_with_audio(
    provider: llm.Provider,
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test a call using an audio file loaded from disk."""

    @llm.call(provider=provider, model_id=model_id)
    def transcribe_audio(audio_path: str) -> llm.UserContent:
        return [
            "Repeat exactly what you hear:",
            llm.Audio.from_file(audio_path),
        ]

    with snapshot_test(snapshot, caplog) as snap:
        response = transcribe_audio(HELLO_AUDIO_PATH)
        snap.set_response(response)
