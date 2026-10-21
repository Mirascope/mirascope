"""Tests that every `FinishReason` can be mapped to a GenAI finish reason."""

from __future__ import annotations

import pytest

from mirascope.llm.responses.finish_reason import FinishReason
from mirascope.ops._internal.instrumentation.llm.encode import map_finish_reason


@pytest.mark.parametrize("reason", list(FinishReason))
def test_every_finish_reason_maps(reason: FinishReason) -> None:
    """Instrumentation must not raise for a finish reason the providers can produce."""
    assert map_finish_reason(reason) in {"length", "content_filter"}


def test_context_length_exceeded_maps_to_length() -> None:
    assert map_finish_reason(FinishReason.CONTEXT_LENGTH_EXCEEDED) == "length"


def test_no_finish_reason_maps_to_stop() -> None:
    assert map_finish_reason(None) == "stop"
