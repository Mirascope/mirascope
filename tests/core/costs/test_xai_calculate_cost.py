"""Tests the `_xai_calculate_cost` function."""

from mirascope.core.base.types import CostMetadata
from mirascope.core.costs._xai_calculate_cost import calculate_cost


def test_calculate_cost() -> None:
    """Tests the `calculate_cost` function."""
    assert calculate_cost(CostMetadata(), model="grok-2-latest") is None
    assert (
        calculate_cost(CostMetadata(input_tokens=1, output_tokens=1), model="unknown")
        is None
    )
    assert (
        calculate_cost(CostMetadata(input_tokens=1, output_tokens=1), model="grok-3")
        == 1.4e-5
    )
