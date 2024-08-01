"""Tests the `anthropic._utils.calculate_cost` function."""

from mirascope.core.anthropic._utils._calculate_cost import calculate_cost


def test_calculate_cost() -> None:
    """Tests the `calculate_cost` function."""
    assert calculate_cost(None, None, model="claude-3-5-sonnet-20240620") is None
    assert calculate_cost(1, 1, model="unknown") is None
    assert calculate_cost(1, 1, model="claude-3-5-sonnet-20240620") == 0.000018
