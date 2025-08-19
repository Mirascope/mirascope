"""Test utilities for response testing."""

from mirascope import llm


def response_snapshot_dict(response: llm.Response) -> dict:
    dict_copy = response.__dict__.copy()
    dict_copy.pop("raw")
    dict_copy.pop("format_type")
    return dict_copy


def stream_response_snapshot_dict(
    response: llm.StreamResponse | llm.AsyncStreamResponse,
) -> dict:
    """Return a dictionary of public fields for snapshot testing.

    This excludes private fields like _chunk_iterator, _current_content, etc.
    and raw data that's provider-specific and not useful for snapshots.
    """
    return {
        "provider": response.provider,
        "model": response.model,
        "finish_reason": response.finish_reason,
        "messages": list(response.messages),
        "content": list(response.content),
        "texts": list(response.texts),
        "tool_calls": list(response.tool_calls),
        "thinkings": list(response.thinkings),
        "consumed": response.consumed,
        "chunks": list(response.chunks),
    }
