"""Tests the `_gemini_calculate_cost` function."""

from mirascope.core.base.types import CostMetadata
from mirascope.core.costs._gemini_calculate_cost import calculate_cost


def test_calculate_cost() -> None:
    """Tests the `calculate_cost` function."""
    assert calculate_cost(CostMetadata(), model="gemini-1.5-flash") is None
    assert (
        calculate_cost(CostMetadata(input_tokens=1, output_tokens=1), model="unknown")
        is None
    )
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1, output_tokens=1), model="gemini-1.5-flash"
        )
        == 0.000000375
    )
