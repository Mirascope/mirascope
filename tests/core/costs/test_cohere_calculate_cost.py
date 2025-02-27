"""Tests the `cohere._utils.calculate_cost` function."""

from mirascope.core.base.types import CostMetadata
from mirascope.core.costs._cohere_calculate_cost import calculate_cost


def test_calculate_cost() -> None:
    """Tests the `calculate_cost` function."""
    assert calculate_cost(CostMetadata(), model="command-r-plus") is None
    assert (
        calculate_cost(CostMetadata(input_tokens=1, output_tokens=1), model="unknown")
        is None
    )
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1, output_tokens=1), model="command-r-plus"
        )
        == 1.8e-05
    )
