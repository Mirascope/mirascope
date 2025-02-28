"""Tests the `_openai_calculate_cost` function."""

from mirascope.core.base.types import CostMetadata, ImageMetadata
from mirascope.core.costs._openai_calculate_cost import calculate_cost


def test_calculate_cost() -> None:
    """Tests the `calculate_cost` function."""
    # Test empty/invalid inputs
    assert calculate_cost(CostMetadata(), model="gpt-4o-mini") == 0
    assert (
        calculate_cost(CostMetadata(input_tokens=1, output_tokens=1), model="unknown")
        is None
    )

    # Test basic token calculation
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1, output_tokens=1), model="gpt-4o-mini"
        )
        == 0.00000075
    )

    # Test different models
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1000, output_tokens=500), model="gpt-4o"
        )
        == 1000 * 0.0000025 + 500 * 0.00001
    )

    assert (
        calculate_cost(
            CostMetadata(input_tokens=1000, output_tokens=500),
            model="gpt-3.5-turbo-0125",
        )
        == 1000 * 0.0000005 + 500 * 0.0000015
    )

    # Test with cached tokens
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1000, output_tokens=500, cached_tokens=200),
            model="gpt-4o",
        )
        == 1000 * 0.0000025 + 200 * 0.00000125 + 500 * 0.00001
    )

    # Test with images (low detail)
    assert (
        calculate_cost(
            CostMetadata(
                input_tokens=1000,
                output_tokens=500,
                images=[ImageMetadata(width=800, height=600, detail="low")],
            ),
            model="gpt-4-vision-preview",
        )
        == (1000 + 85) * 0.00001 + 500 * 0.00003
    )

    # Test with images (high detail)
    assert (
        calculate_cost(
            CostMetadata(
                input_tokens=1000,
                output_tokens=500,
                images=[ImageMetadata(width=1024, height=1024, detail="high")],
            ),
            model="gpt-4-vision-preview",
        )
        == (1000 + 85 + (4 * 170)) * 0.00001 + 500 * 0.00003
    )

    # Test with precalculated image tokens
    assert (
        calculate_cost(
            CostMetadata(
                input_tokens=1000,
                output_tokens=500,
                images=[ImageMetadata(width=800, height=600, tokens=200)],
            ),
            model="gpt-4-vision-preview",
        )
        == (1000 + 200) * 0.00001 + 500 * 0.00003
    )

    # Test with multiple images of different sizes
    assert (
        calculate_cost(
            CostMetadata(
                input_tokens=1000,
                output_tokens=500,
                images=[
                    ImageMetadata(width=512, height=512, detail="low"),
                    ImageMetadata(width=1024, height=768, detail="high"),
                ],
            ),
            model="gpt-4-vision-preview",
        )
        == 0.0335
    )

    # Test batch mode for regular models (50% discount)
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1000, output_tokens=500, batch_mode=True),
            model="gpt-4o",
        )
        == (1000 * 0.0000025 + 500 * 0.00001) * 0.5
    )

    # Test batch mode with cached tokens
    assert (
        calculate_cost(
            CostMetadata(
                input_tokens=1000, output_tokens=500, cached_tokens=200, batch_mode=True
            ),
            model="gpt-4o",
        )
        == (1000 * 0.0000025 + 200 * 0.00000125 + 500 * 0.00001) * 0.5
    )

    # Test embedding models
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1000, output_tokens=0),
            model="text-embedding-3-small",
        )
        == 1000 * 0.00000002
    )

    # Test batch mode for embedding models (special pricing)
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1000, output_tokens=0, batch_mode=True),
            model="text-embedding-3-small",
        )
        == 1000 * 0.00000001
    )

    # Test with explicitly provided cost value
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1000, output_tokens=500, cost=0.123),
            model="gpt-4o",
        )
        == 0.123
    )

    # Test o1 model pricing
    assert (
        calculate_cost(CostMetadata(input_tokens=1000, output_tokens=500), model="o1")
        == 1000 * 0.000015 + 500 * 0.00006
    )

    # Test realtime models
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1000, output_tokens=500),
            model="gpt-4o-realtime-preview",
        )
        == 1000 * 0.000005 + 500 * 0.00002
    )
