"""Tests for the Context class."""

from mirascope import llm


def test_context_can_have_deps() -> None:
    """Test that Context can hold dependencies."""
    context = llm.Context[int](deps=42)

    assert context.deps == 42
