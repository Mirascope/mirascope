"""Tests the `groq._utils.calculate_cost` function."""

from mirascope.core.groq._utils._calculate_cost import calculate_cost


def test_calculate_cost() -> None:
    """Tests the `calculate_cost` function."""
    assert (
        calculate_cost(None, None, model="llama3-groq-70b-8192-tool-use-preview")
        is None
    )
    assert calculate_cost(1, 1, model="unknown") is None
    assert (
        calculate_cost(1, 1, model="llama3-groq-70b-8192-tool-use-preview") == 1.78e-6
    )
