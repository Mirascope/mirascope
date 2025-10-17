"""Test utilities for response testing."""

from typing import Any

from mirascope import llm


def format_snapshot(
    format: llm.formatting.Format[llm.formatting.FormattableT] | None,
) -> dict | None:
    if format is None:
        return None

    return {
        "name": format.name,
        "description": format.description,
        "schema": format.schema,
        "mode": format.mode,
        "formatting_instructions": format.formatting_instructions,
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
    dict_copy.pop("format")
    dict_copy["format"] = format_snapshot(response.format)
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
        "format": format_snapshot(response.format),
        "tools": [tool_snapshot(tool) for tool in response.toolkit.tools],
        "n_chunks": len(
            response.chunks
        ),  # Just snapshot the number of chunks to minimize bloat. Chunk reconstruction is tested separately.
    }


def exception_snapshot_dict(exception: Exception) -> dict:
    """Convert an exception to a dictionary for snapshot testing.

    (inline-snapshot is not able to serialize and reproduce Exceptions.)"""
    if exception.args:
        arg = exception.args[0]
        # Anthropic/OpenAI will raise an APIConnectionError with "Connection error"
        # in args; with google CannotOverwriteExistingCassetteException gets raised
        if "Connection error" in arg or "Can't overwrite existing cassette" in arg:
            raise exception

    return {
        "type": type(exception).__name__,
        **{
            attr: str(getattr(exception, attr))
            for attr in dir(exception)
            if not attr.startswith("_") and not callable(getattr(exception, attr))
        },
    }
