"""A module for utility functions for working with Cohere."""

from typing import Optional

from cohere.types.api_meta_billed_units import ApiMetaBilledUnits


def cohere_api_calculate_cost(
    usage: ApiMetaBilledUnits, model="command-r"
) -> Optional[float]:
    """Calculate the cost of a completion using the Cohere API.

    https://cohere.com/pricing

    Model              Input               Output
    command-r          $0.5 / 1M tokens	   $1.5 / 1M tokens
    command-r-plus     $3 / 1M tokens	   $15 / 1M tokens
    """
    pricing = {
        "command-r": {
            "prompt": 0.000_000_5,
            "completion": 0.000_001_5,
        },
        "command-r-plus": {
            "prompt": 0.000_003,
            "completion": 0.000_015,
        },
    }

    try:
        model_pricing = pricing[model]
    except KeyError:
        return None

    input_tokens = usage.input_tokens or 0
    output_tokens = usage.output_tokens or 0
    prompt_cost = input_tokens * model_pricing["prompt"]
    completion_cost = output_tokens * model_pricing["completion"]
    total_cost = prompt_cost + completion_cost

    return total_cost
