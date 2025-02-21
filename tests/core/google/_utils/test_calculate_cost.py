"""Tests the `google._utils.calculate_cost` function."""

from mirascope.core.google._utils._calculate_cost import calculate_cost


def test_calculate_cost() -> None:
    """Tests the `calculate_cost` function."""
    assert calculate_cost(None, None, None, model="google-1.5-flash") is None
    assert calculate_cost(1, None, 1, model="unknown") is None
    assert calculate_cost(1, None, 1, model="gemini-1.5-flash") == 0.000000375
