"""Tests the `azure._utils.calculate_cost` function."""

from mirascope.core.azure._utils._calculate_cost import calculate_cost


def test_calculate_cost() -> None:
    """Tests the `calculate_cost` function."""
    assert calculate_cost(None, None, model="gpt-4o-mini") is None
    assert calculate_cost(1, 1, model="unknown") is None
    assert calculate_cost(1, 1, model="gpt-4o-mini") is None
