"""Tests the `_groq_calculate_cost` function."""

from mirascope.core.base.types import CostMetadata, ImageMetadata
from mirascope.core.costs._groq_calculate_cost import calculate_cost


def test_calculate_cost() -> None:
    """Tests the `calculate_cost` function."""
    assert (
        calculate_cost(CostMetadata(), model="llama3-groq-70b-8192-tool-use-preview")
        is None
    )
    assert (
        calculate_cost(CostMetadata(input_tokens=1, output_tokens=1), model="unknown")
        is None
    )
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1, output_tokens=1),
            model="llama3-groq-70b-8192-tool-use-preview",
        )
        == 1.78e-6
    )


def test_calculate_cost_different_models() -> None:
    """Tests the `calculate_cost` function with different models."""
    # Test with mixtral model (default)
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1000, output_tokens=500),
        )
        == 0.00000024 * 1000 + 0.00000024 * 500
    )

    # Test with llama model
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1000, output_tokens=500),
            model="llama3-70b-8192",
        )
        == 0.00000059 * 1000 + 0.00000079 * 500
    )

    # Test with gemma model
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1000, output_tokens=500),
            model="gemma-7b-it",
        )
        == 0.00000007 * 1000 + 0.00000007 * 500
    )


def test_calculate_cost_vision_models() -> None:
    """Tests the `calculate_cost` function with vision models."""
    # Test vision model without images
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1000, output_tokens=500),
            model="llama-3.2-11b-vision-preview",
        )
        == 0.00000018 * 1000 + 0.00000018 * 500
    )

    # Test vision model with one image
    assert (
        calculate_cost(
            CostMetadata(
                input_tokens=1000,
                output_tokens=500,
                images=[ImageMetadata(width=0, height=0)],
            ),
            model="llama-3.2-11b-vision-preview",
        )
        == 0.00000018 * 1000 + 0.00000018 * 500 + 0.00000018 * 6400
    )

    # Test vision model with multiple images
    assert (
        calculate_cost(
            CostMetadata(
                input_tokens=1000,
                output_tokens=500,
                images=[
                    ImageMetadata(width=0, height=0),
                    ImageMetadata(width=0, height=0),
                    ImageMetadata(width=0, height=0),
                ],
            ),
            model="llama-3.2-90b-vision-preview",
        )
        == 0.01863
    )

    # Test with images on non-vision model (should ignore images)
    assert (
        calculate_cost(
            CostMetadata(
                input_tokens=1000,
                output_tokens=500,
                images=[ImageMetadata(width=0, height=0)],
            ),
            model="mixtral-8x7b-32768",
        )
        == 0.00000024 * 1000 + 0.00000024 * 500
    )


def test_calculate_cost_none_values() -> None:
    """Tests the `calculate_cost` function with None values."""
    # Test with None input_tokens
    assert (
        calculate_cost(
            CostMetadata(input_tokens=None, output_tokens=500),
            model="mixtral-8x7b-32768",
        )
        is None
    )

    # Test with None output_tokens
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1000, output_tokens=None),
            model="mixtral-8x7b-32768",
        )
        is None
    )


def test_calculate_cost_asymmetric_pricing() -> None:
    """Tests the `calculate_cost` function with models having asymmetric pricing."""
    # Test with model where input and output costs differ
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1000, output_tokens=500),
            model="llama-3.3-70b-specdec",
        )
        == 0.00000059 * 1000 + 0.00000099 * 500
    )

    # Test with deepseek model
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1000, output_tokens=500),
            model="deepseek-r1-distill-llama-70b",
        )
        == 0.00000075 * 1000 + 0.00000099 * 500
    )
