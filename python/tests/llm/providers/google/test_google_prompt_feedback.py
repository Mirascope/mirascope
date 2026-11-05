"""Tests that a prompt blocked by Gemini decodes as a refusal."""

from google.genai import types as genai_types

from mirascope.llm.providers.google._utils.decode import decode_response, decode_stream
from mirascope.llm.responses import FinishReason, FinishReasonChunk


def _blocked_response() -> genai_types.GenerateContentResponse:
    # When Gemini rejects the prompt it returns no candidates at all and
    # explains why in `prompt_feedback`.
    return genai_types.GenerateContentResponse(
        candidates=None,
        prompt_feedback=genai_types.GenerateContentResponsePromptFeedback(
            block_reason=genai_types.BlockedReason.PROHIBITED_CONTENT,
        ),
    )


def test_decode_response_blocked_prompt_is_refusal() -> None:
    message, finish_reason, _ = decode_response(
        _blocked_response(), "google/gemini-2.5-flash", include_thoughts=False
    )

    assert message.content == []
    assert finish_reason == FinishReason.REFUSAL


def test_decode_response_without_block_reason_has_no_finish_reason() -> None:
    _, finish_reason, _ = decode_response(
        genai_types.GenerateContentResponse(
            candidates=[
                genai_types.Candidate(
                    content=genai_types.Content(
                        role="model", parts=[genai_types.Part(text="hi")]
                    )
                )
            ],
            prompt_feedback=genai_types.GenerateContentResponsePromptFeedback(),
        ),
        "google/gemini-2.5-flash",
        include_thoughts=False,
    )

    assert finish_reason is None


def test_decode_stream_blocked_prompt_is_refusal() -> None:
    chunks = list(decode_stream(iter([_blocked_response()]), include_thoughts=False))

    finish = [c for c in chunks if isinstance(c, FinishReasonChunk)]
    assert [c.finish_reason for c in finish] == [FinishReason.REFUSAL]
