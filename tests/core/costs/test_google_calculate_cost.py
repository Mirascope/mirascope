"""Tests the `_google_calculate_cost` function."""

from math import isclose

from mirascope.core.base.types import CostMetadata, GoogleMetadata
from mirascope.core.costs._google_calculate_cost import (
    GEMINI_API_PRICING,
    VERTEX_AI_PRICING,
    _calculate_context_cache_cost,
    _calculate_grounding_cost,
    _calculate_standard_gemini_cost,
    _calculate_vertex_1_5_cost,
    _calculate_vertex_2_0_cost,
    calculate_cost,
)


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


def test_context_cache_cost_none_tokens():
    meta = CostMetadata(
        input_tokens=100,
        output_tokens=100,
        context_cache_tokens=None,
        context_cache_hours=2,
    )
    pricing = GEMINI_API_PRICING["gemini-1.5-pro"]
    cost = _calculate_context_cache_cost(
        meta, pricing, "gemini-1.5-pro", use_vertex_ai=False
    )
    assert cost == 0.0


def test_context_cache_cost_none_hours():
    meta = CostMetadata(
        input_tokens=100,
        output_tokens=100,
        context_cache_tokens=10000,
        context_cache_hours=None,
    )
    pricing = GEMINI_API_PRICING["gemini-1.5-pro"]
    cost = _calculate_context_cache_cost(
        meta, pricing, "gemini-1.5-pro", use_vertex_ai=False
    )
    assert cost == 0.0


def test_context_cache_cost_vertex_2_0():
    meta = CostMetadata(
        input_tokens=100,
        output_tokens=100,
        context_cache_tokens=10000,
        context_cache_hours=2,
    )
    pricing = VERTEX_AI_PRICING[
        "gemini-2.0-flash"
    ]  # cache_storage_per_hour = 0.00000100
    cost = _calculate_context_cache_cost(
        meta, pricing, "gemini-2.0-flash", use_vertex_ai=True
    )
    expected = (
        10000 * pricing.get("cache_storage_per_hour", 0) * 2
    )  # 10000*0.00000100*2 = 0.02
    assert isclose(cost, expected, rel_tol=1e-9)


def test_context_cache_cost_vertex_1_5():
    meta = CostMetadata(
        input_tokens=100,
        output_tokens=100,
        context_cache_tokens=10000,
        context_cache_hours=2,
    )
    pricing = VERTEX_AI_PRICING["gemini-1.5-pro"]  # cache_storage_text = 0.001125
    cost = _calculate_context_cache_cost(
        meta, pricing, "gemini-1.5-pro", use_vertex_ai=True
    )
    expected = 40 * pricing["cache_storage_text"] * 2
    assert isclose(cost, expected, rel_tol=1e-9)


def test_context_cache_cost_standard():
    meta = CostMetadata(
        input_tokens=100,
        output_tokens=100,
        context_cache_tokens=10000,
        context_cache_hours=2,
    )
    pricing = GEMINI_API_PRICING["gemini-1.5-pro"]
    # Standard branch: storage_rate_per_token = 0.000001
    expected = 10000 * 0.000001 * 2  # = 0.02
    cost = _calculate_context_cache_cost(
        meta, pricing, "gemini-1.5-pro", use_vertex_ai=False
    )
    assert isclose(cost, expected, rel_tol=1e-9)


def test_context_cache_cost_standard_flash_8b():
    meta = CostMetadata(
        input_tokens=100,
        output_tokens=100,
        context_cache_tokens=10000,
        context_cache_hours=2,
    )
    pricing = GEMINI_API_PRICING["gemini-1.5-flash-8b"]
    expected = 10000 * 0.00000025 * 2  # = 0.005
    cost = _calculate_context_cache_cost(
        meta, pricing, "gemini-1.5-flash-8b", use_vertex_ai=False
    )
    assert isclose(cost, expected, rel_tol=1e-9)


def test_grounding_cost_no_google():
    meta = CostMetadata(input_tokens=100, output_tokens=100)
    cost = _calculate_grounding_cost(meta, "gemini-2.0-flash")
    assert cost == 0.0


def test_grounding_cost_no_requests():
    meta = CostMetadata(
        input_tokens=100,
        output_tokens=100,
        google=GoogleMetadata(use_vertex_ai=True, grounding_requests=None),
    )
    cost = _calculate_grounding_cost(meta, "gemini-2.0-flash")
    assert cost == 0.0


def test_grounding_cost_free_tier():
    meta = CostMetadata(
        input_tokens=100,
        output_tokens=100,
        google=GoogleMetadata(use_vertex_ai=True, grounding_requests=1500),
    )
    cost = _calculate_grounding_cost(meta, "gemini-2.0-flash")
    assert cost == 0.0


def test_grounding_cost_excess_vertex():
    meta = CostMetadata(
        input_tokens=100,
        output_tokens=100,
        google=GoogleMetadata(use_vertex_ai=True, grounding_requests=2000),
    )
    # Excess = 2000 - 1500 = 500; cost = (500/1000)*35 = 17.5
    cost = _calculate_grounding_cost(meta, "gemini-2.0-flash")
    assert isclose(cost, 17.5, rel_tol=1e-9)


def test_grounding_cost_non_vertex():
    meta = CostMetadata(
        input_tokens=100,
        output_tokens=100,
        google=GoogleMetadata(use_vertex_ai=False, grounding_requests=2000),
    )
    # For non–Vertex AI, no free tier: cost = (2000/1000)*35 = 70
    cost = _calculate_grounding_cost(meta, "gemini-2.0-flash")
    assert isclose(cost, 70.0, rel_tol=1e-9)


def test_grounding_cost_other_model():
    meta = CostMetadata(
        input_tokens=100,
        output_tokens=100,
        google=GoogleMetadata(use_vertex_ai=True, grounding_requests=2000),
    )
    # For a model other than gemini-2.0-flash, excess_requests = grounding_requests = 2000
    cost = _calculate_grounding_cost(meta, "gemini-1.5-flash")
    expected = (2000 / 1000) * 35.0  # = 70.0
    assert isclose(cost, expected, rel_tol=1e-9)


def test_vertex_2_0_cost_non_batch():
    meta = CostMetadata(
        input_tokens=1000,
        output_tokens=500,
        cached_tokens=100,
        context_cache_tokens=None,
        context_cache_hours=None,
        google=GoogleMetadata(use_vertex_ai=True, grounding_requests=None),
        batch_mode=False,
    )
    pricing = VERTEX_AI_PRICING["gemini-2.0-flash"]
    cost = _calculate_vertex_2_0_cost(meta, pricing, "gemini-2.0-flash")
    expected = (
        1000 * pricing["text_input"] + 500 * pricing["output"] + 100 * pricing["cached"]
    )
    # No context cache (tokens None) and grounding cost is 0
    assert isclose(cost, expected, rel_tol=1e-9)


def test_vertex_2_0_cost_batch():
    meta = CostMetadata(
        input_tokens=1000,
        output_tokens=500,
        cached_tokens=100,
        context_cache_tokens=10000,
        context_cache_hours=2,
        google=GoogleMetadata(use_vertex_ai=True, grounding_requests=2000),
        batch_mode=True,
    )
    pricing = VERTEX_AI_PRICING["gemini-2.0-flash"]
    # Compute individual components
    prompt_cost = 1000 * pricing["text_input"]
    completion_cost = 500 * pricing["output"]
    cached_cost = 100 * pricing["cached"]
    context_cache_cost = _calculate_context_cache_cost(
        meta, pricing, "gemini-2.0-flash", True
    )
    grounding_cost = _calculate_grounding_cost(meta, "gemini-2.0-flash")
    # Batch discount applies to prompt, completion, and context cache
    prompt_cost *= 0.5
    completion_cost *= 0.5
    context_cache_cost *= 0.5
    expected = (
        prompt_cost
        + completion_cost
        + cached_cost
        + context_cache_cost
        + grounding_cost
    )
    cost = _calculate_vertex_2_0_cost(meta, pricing, "gemini-2.0-flash")
    assert isclose(cost, expected, rel_tol=1e-9)


def test_vertex_1_5_cost_non_batch():
    meta = CostMetadata(
        input_tokens=1000,
        output_tokens=500,
        cached_tokens=0,
        context_cache_tokens=None,
        context_cache_hours=None,
        google=GoogleMetadata(use_vertex_ai=True, grounding_requests=None),
        batch_mode=False,
    )
    pricing = VERTEX_AI_PRICING["gemini-1.5-pro"]
    # text_cost = (1000*4/1000)*pricing["text_input"]
    # output_cost = (500*4/1000)*pricing["output"]
    expected = (1000 * 4 / 1000) * pricing["text_input"] + (500 * 4 / 1000) * pricing[
        "output"
    ]
    cost = _calculate_vertex_1_5_cost(meta, pricing, "gemini-1.5-pro")
    assert isclose(cost, expected, rel_tol=1e-9)


def test_vertex_1_5_cost_batch():
    meta = CostMetadata(
        input_tokens=1000,
        output_tokens=500,
        cached_tokens=0,
        context_cache_tokens=10000,
        context_cache_hours=2,
        google=GoogleMetadata(use_vertex_ai=True, grounding_requests=2000),
        batch_mode=True,
    )
    pricing = VERTEX_AI_PRICING["gemini-1.5-pro"]
    text_cost = (1000 * 4 / 1000) * pricing["text_input"]
    output_cost = (500 * 4 / 1000) * pricing["output"]
    context_cache_cost = _calculate_context_cache_cost(
        meta, pricing, "gemini-1.5-pro", True
    )
    grounding_cost = _calculate_grounding_cost(meta, "gemini-1.5-pro")
    text_cost *= 0.5
    output_cost *= 0.5
    context_cache_cost *= 0.5
    expected = text_cost + output_cost + context_cache_cost + grounding_cost
    cost = _calculate_vertex_1_5_cost(meta, pricing, "gemini-1.5-pro")
    assert isclose(cost, expected, rel_tol=1e-9)


def test_standard_gemini_cost_short_context():
    meta = CostMetadata(
        input_tokens=1000,
        output_tokens=500,
        cached_tokens=200,
        context_cache_tokens=10000,
        context_cache_hours=2,
        google=None,
        batch_mode=False,
    )
    pricing = GEMINI_API_PRICING["gemini-1.5-pro"]
    use_long_context = False  # input_tokens is low and context_length is not set
    prompt_price = pricing["prompt_short"]
    cached_price = pricing["cached"]
    completion_price = pricing["completion_short"]
    prompt_cost = 1000 * prompt_price
    cached_cost = 200 * cached_price
    completion_cost = 500 * completion_price
    context_cache_cost = _calculate_context_cache_cost(
        meta, pricing, "gemini-1.5-pro", use_vertex_ai=False
    )
    grounding_cost = _calculate_grounding_cost(meta, "gemini-1.5-pro")
    expected = (
        prompt_cost
        + cached_cost
        + completion_cost
        + context_cache_cost
        + grounding_cost
    )
    cost = _calculate_standard_gemini_cost(
        meta, pricing, "gemini-1.5-pro", use_long_context
    )
    assert isclose(cost, expected, rel_tol=1e-9)


def test_standard_gemini_cost_long_context():
    meta = CostMetadata(
        input_tokens=1000,
        output_tokens=500,
        cached_tokens=200,
        context_cache_tokens=10000,
        context_cache_hours=2,
        context_length=130000,  # triggers long context pricing
        google=None,
        batch_mode=False,
    )
    pricing = GEMINI_API_PRICING["gemini-1.5-pro"]
    use_long_context = True
    prompt_price = pricing["prompt_long"]
    cached_price = pricing["cached"]
    completion_price = pricing["completion_long"]
    prompt_cost = 1000 * prompt_price
    cached_cost = 200 * cached_price
    completion_cost = 500 * completion_price
    context_cache_cost = _calculate_context_cache_cost(
        meta, pricing, "gemini-1.5-pro", use_vertex_ai=False
    )
    grounding_cost = _calculate_grounding_cost(meta, "gemini-1.5-pro")
    expected = (
        prompt_cost
        + cached_cost
        + completion_cost
        + context_cache_cost
        + grounding_cost
    )
    cost = _calculate_standard_gemini_cost(
        meta, pricing, "gemini-1.5-pro", use_long_context
    )
    assert isclose(cost, expected, rel_tol=1e-9)


def test_calculate_cost_vertex_1_5():
    meta = CostMetadata(
        input_tokens=1000,
        output_tokens=500,
        google=GoogleMetadata(use_vertex_ai=True, grounding_requests=0),
        batch_mode=False,
    )
    pricing = VERTEX_AI_PRICING["gemini-1.5-pro"]
    expected = _calculate_vertex_1_5_cost(meta, pricing, "gemini-1.5-pro")
    cost = calculate_cost(meta, "gemini-1.5-pro")
    assert isclose(cost, expected, rel_tol=1e-9)  # pyright: ignore [reportArgumentType]


def test_calculate_cost_vertex_2_0() -> None:
    """Test that calculate_cost uses the Vertex AI branch for Gemini 2.0 models."""
    meta = CostMetadata(
        input_tokens=1000,
        output_tokens=500,
        cached_tokens=100,
        context_cache_tokens=2000,
        context_cache_hours=1,
        google=GoogleMetadata(use_vertex_ai=True, grounding_requests=0),
        batch_mode=False,
    )
    model = "gemini-2.0-flash"  # a model name starting with "gemini-2.0"
    pricing = VERTEX_AI_PRICING[model]
    expected = _calculate_vertex_2_0_cost(meta, pricing, model)
    cost = calculate_cost(meta, model)
    assert isclose(cost, expected, rel_tol=1e-9)  # pyright: ignore [reportArgumentType]


def test_calculate_cost_vertex_unsupported_model() -> None:
    """Test that calculate_cost correctly dispatches to None for unsupported models."""

    meta = CostMetadata(
        input_tokens=2000,
        output_tokens=1000,
        cached_tokens=50,
        context_cache_tokens=5000,
        context_cache_hours=1,
        google=GoogleMetadata(use_vertex_ai=True, grounding_requests=1500),
        batch_mode=True,
    )
    model = "unsupported"
    assert calculate_cost(meta, model) is None
