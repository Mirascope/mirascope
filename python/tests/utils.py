"""Test utilities for response testing."""

import contextlib
import logging
from collections.abc import Generator
from typing import Any, TypeAlias

import pytest

from mirascope import llm

Snapshot: TypeAlias = Any  # Alias to avoid Ruff lint errors


def format_snapshot(
    format: llm.formatting.Format[llm.formatting.FormattableT] | None,
) -> dict[str, Any] | None:
    if format is None:
        return None

    return {
        "name": format.name,
        "description": format.description,
        "schema": format.schema,
        "mode": format.mode,
        "formatting_instructions": format.formatting_instructions,
    }


def tool_snapshot(
    tool: llm.tools.AnyToolSchema,
) -> dict[str, Any]:
    return {
        "name": tool.name,
        "description": tool.description,
        "parameters": tool.parameters.model_dump_json(indent=2),
        "strict": tool.strict,
    }


def usage_snapshot(usage: llm.Usage | None) -> dict[str, int | None] | None:
    if not usage:
        return None
    dict_copy = usage.__dict__.copy()
    dict_copy["total_tokens"] = usage.total_tokens
    dict_copy["raw"] = str(usage.raw)  # Useful for sanity checking snapshots
    return dict_copy


def response_snapshot_dict(
    response: llm.responses.RootResponse[Any, Any],
) -> dict[str, Any]:
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
    dict_copy["usage"] = usage_snapshot(response.usage)
    dict_copy.pop("toolkit")
    dict_copy["tools"] = [tool_snapshot(tool) for tool in response.toolkit.tools]
    return dict_copy


def stream_response_snapshot_dict(
    response: llm.StreamResponse[Any]
    | llm.AsyncStreamResponse[Any]
    | llm.ContextStreamResponse[Any, Any]
    | llm.AsyncContextStreamResponse[Any, Any],
) -> dict[str, Any]:
    """Return a dictionary of public fields for snapshot testing.

    This excludes private fields like _chunk_iterator, _current_content, etc.
    and raw data that's provider-specific and not useful for snapshots.
    """
    return {
        "provider_id": response.provider_id,
        "model_id": response.model_id,
        "provider_model_name": response.provider_model_name,
        "finish_reason": response.finish_reason,
        "messages": list(response.messages),
        "format": format_snapshot(response.format),
        "tools": [tool_snapshot(tool) for tool in response.toolkit.tools],
        "usage": usage_snapshot(response.usage),
        "n_chunks": len(
            response.chunks
        ),  # Just snapshot the number of chunks to minimize bloat. Chunk reconstruction is tested separately.
    }


def exception_snapshot_dict(exception: Exception) -> dict[str, Any]:
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


class SnapshotDict(dict[str, Any]):
    """Dictionary with convenience method for snapshotting responses."""

    def set_response(
        self,
        response: (
            llm.Response[Any]
            | llm.AsyncResponse[Any]
            | llm.StreamResponse[Any]
            | llm.AsyncStreamResponse[Any]
            | llm.ContextResponse[Any, Any]
            | llm.AsyncContextResponse[Any, Any]
            | llm.ContextStreamResponse[Any, Any]
            | llm.AsyncContextStreamResponse[Any, Any]
        ),
    ) -> None:
        """Add a response to the snapshot, auto-detecting the type."""
        if isinstance(
            response,
            llm.StreamResponse
            | llm.AsyncStreamResponse
            | llm.ContextStreamResponse
            | llm.AsyncContextStreamResponse,
        ):
            self["response"] = stream_response_snapshot_dict(response)
        else:
            self["response"] = response_snapshot_dict(response)


@contextlib.contextmanager
def snapshot_test(
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture | None = None,
    log_level: int = logging.WARNING,
    extra_exceptions: list[type[Exception]] | None = None,
) -> Generator[SnapshotDict, None, None]:
    """Context manager for exception-safe snapshot testing with optional logging.

    Usage:
        with snapshot_test(snapshot) as snap:
            response = call()
            snap.set_response(response)
            assert "4242" in response.pretty()

        with snapshot_test(snapshot, caplog) as snap:
            response = call()
            snap.set_response(response)

        with snapshot_test(snapshot, extra_exceptions=[ValueError, KeyError]) as snap:
            response = call()
            snap.set_response(response)
    """
    snap = SnapshotDict()

    exceptions_to_catch = (NotImplementedError, llm.FeatureNotSupportedError)
    if extra_exceptions:
        exceptions_to_catch = (*exceptions_to_catch, *extra_exceptions)

    context = caplog.at_level(log_level) if caplog else contextlib.nullcontext()

    with context:
        try:
            yield snap
        except exceptions_to_catch as e:
            snap["exception"] = exception_snapshot_dict(e)
        finally:
            if caplog:
                logs = [
                    record.message
                    for record in caplog.records
                    if record.levelno >= log_level
                ]
                if logs:
                    snap["logs"] = logs

            assert dict(snap) == snapshot
