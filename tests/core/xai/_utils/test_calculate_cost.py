"""Tests the `xai._utils.calculate_cost` function."""

from mirascope.core.xai._utils._calculate_cost import calculate_cost


def test_calculate_cost() -> None:
    """Tests the `calculate_cost` function."""
    assert calculate_cost(None, None, None, model="grok-2-latest") is None
    assert calculate_cost(1, None, 1, model="unknown") is None
    assert calculate_cost(1, None, 1, model="grok-3") == 1.4e-5
