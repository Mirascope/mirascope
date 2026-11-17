"""Tests that Gemini's tool-use prompt tokens count as input tokens."""

from google.genai import types as genai_types

from mirascope.llm.providers.google._utils.decode import decode_response, decode_stream
from mirascope.llm.responses import UsageDeltaChunk


def _usage_metadata(
    *, tool_use: int | None, candidates: int = 5
) -> genai_types.GenerateContentResponseUsageMetadata:
    return genai_types.GenerateContentResponseUsageMetadata(
        prompt_token_count=100,
        tool_use_prompt_token_count=tool_use,
        candidates_token_count=candidates,
        total_token_count=100 + (tool_use or 0) + candidates,
    )


def _response(
    usage_metadata: genai_types.GenerateContentResponseUsageMetadata,
    finish_reason: genai_types.FinishReason | None = genai_types.FinishReason.STOP,
) -> genai_types.GenerateContentResponse:
    return genai_types.GenerateContentResponse(
        candidates=[
            genai_types.Candidate(
                content=genai_types.Content(
                    role="model", parts=[genai_types.Part(text="answer")]
                ),
                finish_reason=finish_reason,
            )
        ],
        usage_metadata=usage_metadata,
    )


def test_decode_response_counts_tool_use_prompt_tokens_as_input() -> None:
    _, _, usage = decode_response(
        _response(_usage_metadata(tool_use=40)),
        "google/gemini-2.5-flash",
        include_thoughts=False,
    )

    assert usage is not None
    assert usage.input_tokens == 140
    assert usage.output_tokens == 5
    assert usage.total_tokens == 145


def test_decode_response_without_tool_use_prompt_tokens_is_unchanged() -> None:
    _, _, usage = decode_response(
        _response(_usage_metadata(tool_use=None)),
        "google/gemini-2.5-flash",
        include_thoughts=False,
    )

    assert usage is not None
    assert usage.input_tokens == 100


def test_decode_stream_counts_tool_use_prompt_tokens_as_input() -> None:
    # Gemini reports running totals, so the second chunk adds only the growth.
    chunks = list(
        decode_stream(
            iter(
                [
                    _response(_usage_metadata(tool_use=20, candidates=2), None),
                    _response(_usage_metadata(tool_use=40, candidates=5)),
                ]
            ),
            include_thoughts=False,
        )
    )

    deltas = [c for c in chunks if isinstance(c, UsageDeltaChunk)]
    assert sum(d.input_tokens for d in deltas) == 140
    assert sum(d.output_tokens for d in deltas) == 5
