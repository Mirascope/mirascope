"""Test utilities for response testing."""

from typing import Any, cast

from mirascope import llm


def get_format(x: type[llm.formatting.FormatT]) -> llm.FormatInfo:
    assert hasattr(x, "__mirascope_format_info__")
    format = cast(llm.formatting.Formattable, x).__mirascope_format_info__
    assert isinstance(format, llm.formatting.FormatInfo)
    return format


def response_snapshot_dict(response: llm.responses.RootResponse[Any, Any]) -> dict:
    dict_copy = response.__dict__.copy()

    # Remove raw response because it is too noisy (test separately if needed)
    dict_copy.pop("raw")

    # remove content, texts, thoughts, and tool calls because they are derived properties
    # from the content of the final assistant message in the messages array. Thus, they
    # are fully redundant with that field and including them only serves to bloat the
    # snapshot. test_response and test_stream_response test that these fields are
    # setup correctly.
    dict_copy.pop("content")
    dict_copy.pop("texts")
    dict_copy.pop("thoughts")
    dict_copy.pop("tool_calls")

    # Remove format_type and toolkit because they are difficult to snapshot
    # (should be tested separately where appropriate)
    dict_copy.pop("format_type")  # Difficult to snapshot, test separately
    dict_copy.pop("toolkit")  # Tools are difficult to snapshot
    return dict_copy


def stream_response_snapshot_dict(
    response: llm.StreamResponse[Any]
    | llm.AsyncStreamResponse[Any]
    | llm.ContextStreamResponse[Any, Any]
    | llm.AsyncContextStreamResponse[Any, Any],
) -> dict:
    """Return a dictionary of public fields for snapshot testing.

    This excludes private fields like _chunk_iterator, _current_content, etc.
    and raw data that's provider-specific and not useful for snapshots.
    """
    return {
        "provider": response.provider,
        "model_id": response.model_id,
        "finish_reason": response.finish_reason,
        "messages": list(response.messages),
        "n_chunks": len(
            response.chunks
        ),  # Just snapshot the number of chunks to minimize bloat. Chunk reconstruction is tested separately.
    }
