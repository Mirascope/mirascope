"""Tests the `_google_calculate_cost` function."""

from mirascope.core.base.types import CostMetadata, GoogleMetadata
from mirascope.core.costs._google_calculate_cost import calculate_cost


def test_calculate_cost() -> None:
    """Tests the `calculate_cost` function."""
    # Test invalid inputs
    assert calculate_cost(CostMetadata(), model="google-1.5-flash") is None
    assert (
        calculate_cost(CostMetadata(input_tokens=1, output_tokens=1), model="unknown")
        is None
    )

    # Test basic Gemini 1.5 Flash model
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1, output_tokens=1), model="gemini-1.5-flash"
        )
        == 0.000000375
    )

    # Test short context pricing
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1000, output_tokens=500), model="gemini-1.5-pro"
        )
        == 1000 * 0.00000125 + 500 * 0.000005
    )

    # Test long context pricing (input > 128K tokens)
    assert (
        calculate_cost(
            CostMetadata(input_tokens=130000, output_tokens=1000),
            model="gemini-1.5-pro",
        )
        == 130000 * 0.0000025 + 1000 * 0.00001
    )

    # Test with cached tokens
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1000, output_tokens=500, cached_tokens=200),
            model="gemini-1.5-pro",
        )
        == 1000 * 0.00000125 + 500 * 0.000005 + 200 * 0.000000625
    )

    # Test context cache costs
    assert (
        calculate_cost(
            CostMetadata(
                input_tokens=1000,
                output_tokens=500,
                context_cache_tokens=10000,
                context_cache_hours=2,
            ),
            model="gemini-1.5-pro",
        )
        == 1000 * 0.00000125 + 500 * 0.000005 + 10000 * 0.000001 * 2
    )

    # Test Vertex AI pricing for Gemini 2.0
    assert (
        calculate_cost(
            CostMetadata(
                input_tokens=1000,
                output_tokens=500,
                google=GoogleMetadata(use_vertex_ai=True),
            ),
            model="gemini-2.0-flash",
        )
        == 1000 * 0.00000015 + 500 * 0.0000006
    )

    # Test batch mode discount (50% for Vertex AI)
    assert (
        calculate_cost(
            CostMetadata(
                input_tokens=1000,
                output_tokens=500,
                batch_mode=True,
                google=GoogleMetadata(use_vertex_ai=True),
            ),
            model="gemini-2.0-flash",
        )
        == (1000 * 0.00000015 + 500 * 0.0000006) * 0.5
    )

    # Test with grounding requests (for Gemini 2.0 with Vertex AI)
    assert (
        calculate_cost(
            CostMetadata(
                input_tokens=1000,
                output_tokens=500,
                google=GoogleMetadata(use_vertex_ai=True, grounding_requests=2000),
            ),
            model="gemini-2.0-flash",
        )
        == 1000 * 0.00000015 + 500 * 0.0000006 + (500 / 1000) * 35.0
    )

    # Test free tier for grounding requests (first 1500 requests)
    assert (
        calculate_cost(
            CostMetadata(
                input_tokens=1000,
                output_tokens=500,
                google=GoogleMetadata(use_vertex_ai=True, grounding_requests=1000),
            ),
            model="gemini-2.0-flash",
        )
        == 1000 * 0.00000015 + 500 * 0.0000006
    )

    # Test Gemini 1.0 model pricing
    assert (
        calculate_cost(
            CostMetadata(input_tokens=1000, output_tokens=500), model="gemini-1.0-pro"
        )
        == 1000 * 0.0000005 + 500 * 0.0000015
    )
