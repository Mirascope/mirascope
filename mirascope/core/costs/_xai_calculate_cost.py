"""Calculate the cost of a Grok API call."""

from ..base.types import CostMetadata


def calculate_cost(
    metadata: CostMetadata,
    model: str,
) -> float | None:
    """Calculate the cost of an xAI Grok API call.

    https://docs.x.ai

    Pricing (per 1M tokens):

    Model                     Input              Cached             Output
    grok-3                    $3.50              $0.875             $10.50
    grok-3-latest             $3.50              $0.875             $10.50
    grok-2                    $2.00              $0.50              $6.00
    grok-2-latest             $2.00              $0.50              $6.00
    grok-2-1212               $2.00              $0.50              $6.00
    grok-2-mini               $0.33              $0.083             $1.00
    grok-2-vision-1212        $2.00              $0.50              $6.00
    grok-vision-beta          $5.00              $1.25              $15.00
    grok-beta                 $5.00              $1.25              $15.00

    Args:
        input_tokens: Number of input tokens
        cached_tokens: Number of cached tokens
        output_tokens: Number of output tokens
        model: Model name to use for pricing calculation

    Returns:
        Total cost in USD or None if invalid input
    """
    pricing = {
        "grok-3": {
            "prompt": 0.000_003_5,
            "cached": 0.000_000_875,
            "completion": 0.000_010_5,
        },
        "grok-3-latest": {
            "prompt": 0.000_003_5,
            "cached": 0.000_000_875,
            "completion": 0.000_010_5,
        },
        "grok-2": {
            "prompt": 0.000_002,
            "cached": 0.000_000_5,
            "completion": 0.000_006,
        },
        "grok-latest": {
            "prompt": 0.000_002,
            "cached": 0.000_000_5,
            "completion": 0.000_006,
        },
        "grok-2-1212": {
            "prompt": 0.000_002,
            "cached": 0.000_000_5,
            "completion": 0.000_006,
        },
        "grok-2-mini": {
            "prompt": 0.000_000_33,
            "cached": 0.000_000_083,
            "completion": 0.000_001,
        },
        "grok-2-vision-1212": {
            "prompt": 0.000_002,
            "cached": 0.000_000_5,
            "completion": 0.000_006,
        },
        "grok-vision-beta": {
            "prompt": 0.000_005,
            "cached": 0.000_001_25,
            "completion": 0.000_015,
        },
        "grok-beta": {
            "prompt": 0.000_005,
            "cached": 0.000_001_25,
            "completion": 0.000_015,
        },
    }

    if metadata.input_tokens is None or metadata.output_tokens is None:
        return None

    if metadata.cached_tokens is None:
        metadata.cached_tokens = 0

    try:
        model_pricing = pricing[model]
    except KeyError:
        return None

    prompt_price = model_pricing["prompt"]
    cached_price = model_pricing["cached"]
    completion_price = model_pricing["completion"]

    prompt_cost = metadata.input_tokens * prompt_price
    cached_cost = metadata.cached_tokens * cached_price
    completion_cost = metadata.output_tokens * completion_price
    total_cost = prompt_cost + cached_cost + completion_cost

    return total_cost
