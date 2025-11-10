"""Test utilities for response testing."""

import contextlib
import logging
from collections.abc import Callable, Generator, Sequence
from copy import deepcopy
from dataclasses import replace
from itertools import count
import re
from collections.abc import Generator
from typing import Any, TypeAlias

import pytest

from mirascope import llm

Snapshot: TypeAlias = Any  # Alias to avoid Ruff lint errors


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


def _normalize_xai_tool_call_ids(
        messages: Sequence[llm.messages.Message],
        *,
        provider: llm.Provider | None,
) -> list[llm.messages.Message]:
    """Return messages with deterministic xAI tool call identifiers for snapshots."""
    if provider != "xai":
        return list(messages)

    id_counter = count(1)
    id_map: dict[str, str] = {}
    message_cache: dict[int, llm.messages.Message] = {}

    def _normalized_id(original_id: str) -> str:
        if original_id not in id_map:
            id_map[original_id] = f"tool_call_{next(id_counter):03d}"
        return id_map[original_id]

    def _sanitize_raw_message(raw_message: Any) -> Any:  # noqa: ANN401
        if not isinstance(raw_message, dict):
            return raw_message
        raw_copy = deepcopy(raw_message)
        content_list = raw_copy.get("content")
        if isinstance(content_list, list):
            for item in content_list:
                if (
                        isinstance(item, dict)
                        and item.get("type") == "tool_call"
                        and isinstance(item.get("id"), str)
                ):
                    item["id"] = _normalized_id(item["id"])
                    item["args"] = "[xai tool call args]"
                elif isinstance(item, dict) and item.get("type") == "text":
                    item["text"] = "[xai assistant text]"
                elif isinstance(item, dict) and item.get("type") == "thought":
                    item["thought"] = "[xai assistant thought]"
        tool_calls = raw_copy.get("tool_calls")
        if isinstance(tool_calls, list):
            for tool_call in tool_calls:
                if isinstance(tool_call, dict) and isinstance(tool_call.get("id"), str):
                    tool_call["id"] = _normalized_id(tool_call["id"])
                    if isinstance(tool_call.get("function"), dict):
                        tool_call["function"]["arguments"] = "[xai tool call args]"
        return raw_copy

    def _mask_raw_message_text(raw_message: Any) -> Any:  # noqa: ANN401
        if not isinstance(raw_message, dict):
            return raw_message
        raw_copy = deepcopy(raw_message)
        content_list = raw_copy.get("content")
        if isinstance(content_list, list):
            for item in content_list:
                if isinstance(item, dict) and item.get("type") == "text":
                    item["text"] = "[xai assistant text]"
        return raw_copy

    def _mask_assistant_text(
            message: llm.messages.Message,
    ) -> llm.messages.Message:
        if not isinstance(message, llm.messages.AssistantMessage):
            return message

        new_content = []
        for part in message.content:
            if isinstance(part, llm.content.Text):
                new_content.append(replace(part, text="[xai assistant text]"))
            else:
                new_content.append(part)

        masked_raw = _mask_raw_message_text(message.raw_message)
        return replace(message, content=tuple(new_content), raw_message=masked_raw)

    def _sanitize_message(
            message: llm.messages.Message,
    ) -> llm.messages.Message:
        cached = message_cache.get(id(message))
        if cached is not None:
            return cached

        message_provider = getattr(message, "provider", None)
        if message_provider == "anthropic":
            sanitized = _sanitize_anthropic_message(message)
        elif message_provider in (None, "xai"):
            sanitized = _sanitize_xai_message(
                message, _normalized_id, _sanitize_raw_message
            )
        else:
            sanitized = message

        sanitized = _mask_assistant_text(sanitized)

        message_cache[id(message)] = sanitized
        return sanitized

    return [_sanitize_message(message) for message in messages]


def _sanitize_anthropic_message(message: llm.messages.Message) -> llm.messages.Message:
    """Normalize Anthropic-specific reasoning metadata for snapshots."""

    if isinstance(message, llm.messages.AssistantMessage):
        new_content = []
        for part in message.content:
            if isinstance(part, llm.content.Thought):
                new_content.append(replace(part, thought="[anthropic thinking]"))
            elif isinstance(part, llm.content.ToolCall):
                new_content.append(
                    replace(
                        part, id="[anthropic tool id]", args="[anthropic tool input]"
                    )
                )
            else:
                new_content.append(part)

        raw_message = message.raw_message
        if isinstance(raw_message, dict):
            raw_copy = deepcopy(raw_message)
            content_list = raw_copy.get("content")
            if isinstance(content_list, list):
                for item in content_list:
                    if isinstance(item, dict):
                        if item.get("type") == "thinking":
                            item["signature"] = "[anthropic signature]"
                            item["thinking"] = "[anthropic thinking]"
                        elif item.get("type") == "tool_use":
                            item["id"] = "[anthropic tool id]"
                            item["input"] = "[anthropic tool input]"
            raw_message = raw_copy

        return replace(message, content=tuple(new_content), raw_message=raw_message)

    if isinstance(message, llm.messages.UserMessage):
        new_content = []
        for part in message.content:
            if isinstance(part, llm.content.ToolOutput):
                new_content.append(replace(part, id="[anthropic tool id]"))
            else:
                new_content.append(part)
        return replace(message, content=tuple(new_content))

    return message


def _sanitize_xai_message(
        message: llm.messages.Message,
        normalize_id: Callable[[str], str],
        sanitize_raw: Callable[[Any], Any],
) -> llm.messages.Message:
    """Normalize xAI tool call metadata for snapshots."""

    if isinstance(message, llm.messages.AssistantMessage):
        new_content = []
        for part in message.content:
            if isinstance(part, llm.content.ToolCall):
                new_content.append(
                    replace(part, id=normalize_id(part.id), args="[xai tool call args]")
                )
            elif isinstance(part, llm.content.Text):
                new_content.append(replace(part, text="[xai assistant text]"))
            elif isinstance(part, llm.content.Thought):
                new_content.append(replace(part, thought="[xai assistant thought]"))
            else:
                new_content.append(part)
        return replace(
            message,
            content=tuple(new_content),
            raw_message=sanitize_raw(message.raw_message),
        )

    if isinstance(message, llm.messages.UserMessage):
        new_content = []
        for part in message.content:
            if isinstance(part, llm.content.ToolOutput):
                new_content.append(replace(part, id=normalize_id(part.id)))
            else:
                new_content.append(part)
        return replace(message, content=tuple(new_content))

    return message


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
    dict_copy["messages"] = _normalize_xai_tool_call_ids(
        dict_copy["messages"], provider=response.provider
    )
    if "input_messages" in dict_copy:
        dict_copy["input_messages"] = _normalize_xai_tool_call_ids(
            dict_copy["input_messages"], provider=response.provider
        )
    if "assistant_message" in dict_copy:
        dict_copy["assistant_message"] = _normalize_xai_tool_call_ids(
            [dict_copy["assistant_message"]], provider=response.provider
        )[0]
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
        "messages": _normalize_xai_tool_call_ids(
            list(response.messages), provider=response.provider
        ),
        "format": format_snapshot(response.format),
        "tools": [tool_snapshot(tool) for tool in response.toolkit.tools],
        "n_chunks": (
            "variable" if response.provider == "xai" else len(response.chunks)
        ),  # For xAI, chunk counts fluctuate; record placeholder for stability.
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
