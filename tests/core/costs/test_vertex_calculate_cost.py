"""Tests the `_vertex_calculate_costt` function."""

import pytest

from mirascope.core.base.types import CostMetadata
from mirascope.core.costs._vertex_calculate_cost import calculate_cost


def test_calculate_cost() -> None:
    """Tests the `calculate_cost` function for Vertex AI Gemini models."""
    # Test None inputs
    assert calculate_cost(CostMetadata(), model="gemini-1.5-pro") is None

    # Test unknown model
    assert (
        calculate_cost(CostMetadata(input_tokens=1, output_tokens=1), model="unknown")
        is None
    )

    # Test normal cases with short context
    assert calculate_cost(
        CostMetadata(input_tokens=1000, output_tokens=1000, context_length=100000),
        model="gemini-1.5-flash",
    ) == pytest.approx(0.00009375)
    assert calculate_cost(
        CostMetadata(input_tokens=1000, output_tokens=1000, context_length=100000),
        model="gemini-1.5-pro",
    ) == pytest.approx(0.005)
    assert calculate_cost(
        CostMetadata(input_tokens=1000, output_tokens=1000, context_length=100000),
        model="gemini-1.0-pro",
    ) == pytest.approx(0.0005)

    # Test long context cases
    assert calculate_cost(
        CostMetadata(input_tokens=1000, output_tokens=1000, context_length=150000),
        model="gemini-1.5-flash",
    ) == pytest.approx(0.0001875)
    assert calculate_cost(
        CostMetadata(input_tokens=1000, output_tokens=1000, context_length=150000),
        model="gemini-1.5-pro",
    ) == pytest.approx(0.01)

    # Test Gemini 1.0 Pro with long context (should return None)
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1000, output_tokens=1000, context_length=150000),
            model="gemini-1.0-pro",
        )
        is None
    )

    # Test zero input
    assert (
        calculate_cost(
            CostMetadata(input_tokens=0, output_tokens=0), model="gemini-1.5-pro"
        )
        == 0
    )

    # Test very large input
    large_input = 1_000_000  # 1 million characters
    assert calculate_cost(
        CostMetadata(input_tokens=large_input, output_tokens=large_input),
        model="gemini-1.5-pro",
    ) == pytest.approx(5)

    # Test fractional input
    assert calculate_cost(
        CostMetadata(input_tokens=500.5, output_tokens=500.5), model="gemini-1.5-pro"
    ) == pytest.approx(0.0025025)


def test_calculate_cost_edge_cases() -> None:
    """Tests edge cases for the `calculate_cost` function."""

    # Test exactly 128K context boundary
    assert calculate_cost(
        CostMetadata(input_tokens=1000, output_tokens=1000, context_length=128000),
        model="gemini-1.5-pro",
    ) == pytest.approx(0.005)
    assert calculate_cost(
        CostMetadata(input_tokens=1000, output_tokens=1000, context_length=128001),
        model="gemini-1.5-pro",
    ) == pytest.approx(0.01)
