"""Tests the `_anthropic_calculate_cost` function."""

from mirascope.core.base.types import CostMetadata
from mirascope.core.costs._anthropic_calculate_cost import calculate_cost


def test_calculate_cost() -> None:
    """Tests the `calculate_cost` function."""
    assert calculate_cost(CostMetadata(), model="claude-3-5-sonnet-20240620") is None
    assert (
        calculate_cost(CostMetadata(input_tokens=1, output_tokens=1), model="unknown")
        is None
    )
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1, output_tokens=1),
            model="claude-3-5-sonnet-20240620",
        )
        == 0.000018
    )
