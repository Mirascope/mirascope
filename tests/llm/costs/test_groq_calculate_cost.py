"""Tests the `_groq_calculate_cost` function."""
from mirascope.core.base.types import CostMetadata
from mirascope.llm.costs._groq_calculate_cost import calculate_cost


def test_calculate_cost() -> None:
    """Tests the `calculate_cost` function."""
    assert (
        calculate_cost( CostMetadata(), model="llama3-groq-70b-8192-tool-use-preview")
        is None
    )
    assert calculate_cost(CostMetadata(input_tokens=1, output_tokens=1), model="unknown") is None
    assert (
        calculate_cost(CostMetadata(input_tokens=1, output_tokens=1), model="llama3-groq-70b-8192-tool-use-preview")
        == 1.78e-6
    )
