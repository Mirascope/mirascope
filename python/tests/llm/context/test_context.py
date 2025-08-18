"""Tests for the Context class."""

from mirascope import llm


def test_context_empty_by_default() -> None:
    """Test that Context is initialized with empty messages and no deps by default."""
    ctx = llm.Context()
    assert ctx.messages == []
    assert ctx.deps is None


def test_context_can_have_messages() -> None:
    """Test that Context can be initialized with messages."""
    messages = [llm.messages.user("Hello")]
    context = llm.Context(messages=messages)

    assert context.messages == messages


def test_context_can_have_deps() -> None:
    """Test that Context can hold dependencies."""
    context = llm.Context[int](deps=42)

    assert context.deps == 42
