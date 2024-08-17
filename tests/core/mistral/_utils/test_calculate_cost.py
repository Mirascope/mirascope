"""Tests the `mistral._utils.calculate_cost` function."""

from mirascope.core.mistral._utils._calculate_cost import calculate_cost


def test_calculate_cost() -> None:
    """Tests the `calculate_cost` function."""
    assert calculate_cost(None, None, model="mistral-large-latest") is None
    assert calculate_cost(1, 1, model="unknown") is None
    assert calculate_cost(1, 1, model="mistral-large-latest") == 1.2e-5
