"""Test utilities for response testing."""

from typing import Any, cast

from mirascope import llm


def get_format(x: type[llm.formatting.FormatT]) -> llm.FormatInfo:
    assert hasattr(x, "__mirascope_format_info__")
    format = cast(llm.formatting.Formattable, x).__mirascope_format_info__
    assert isinstance(format, llm.formatting.FormatInfo)
    return format


def format_snapshot_dict(
    format_type: type[llm.formatting.FormatT] | None,
) -> dict | None:
    if format_type is None:
        return None
    format_info = get_format(format_type)
    return {
        "name": format_info.name,
        "description": format_info.description,
        "schema": format_info.schema,
        "mode": format_info.mode,
    }


def tool_snapshot(tool: llm.tools.ToolSchema) -> dict:
    return {
        "name": tool.name,
        "description": tool.description,
        "parameters": tool.parameters.model_dump_json(indent=2),
        "strict": tool.strict,
    }


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

    dict_copy["format_type"] = format_snapshot_dict(response.format_type)
    dict_copy.pop("toolkit")
    dict_copy["tools"] = [tool_snapshot(tool) for tool in response.toolkit.tools]
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
        "format_type": format_snapshot_dict(response.format_type),
        "tools": [tool_snapshot(tool) for tool in response.toolkit.tools],
        "n_chunks": len(
            response.chunks
        ),  # Just snapshot the number of chunks to minimize bloat. Chunk reconstruction is tested separately.
    }


def exception_snapshot_dict(exception: Exception) -> dict:
    """Convert an exception to a dictionary for snapshot testing.

    (inline-snapshot is not able to serialize and reproduce Exceptions.)"""
    return {
        "type": type(exception).__name__,
        **{
            attr: getattr(exception, attr)
            for attr in dir(exception)
            if not attr.startswith("_") and not callable(getattr(exception, attr))
        },
    }
