"""A module for utility functions for working with Anthropic."""
from typing import Optional

from anthropic.types import Usage


def anthropic_api_calculate_cost(
    usage: Usage, model="claude-3-haiku-20240229"
) -> Optional[float]:
    """Calculate the cost of a completion using the Anthropic API.

    https://www.anthropic.com/api

    claude-instant-1.2        $0.80 / 1M tokens   $2.40 / 1M tokens
    claude-2.0                $8.00 / 1M tokens   $24.00 / 1M tokens
    claude-2.1                $8.00 / 1M tokens   $24.00 / 1M tokens
    claude-3-haiku            $0.25 / 1M tokens   $1.25 / 1M tokens
    claude-3-sonnet           $3.00 / 1M tokens   $15.00 / 1M tokens
    claude-3-opus             $15.00 / 1M tokens   $75.00 / 1M tokens
    """
    pricing = {
        "claude-instant-1.2": {
            "prompt": 0.000_000_8,
            "completion": 0.000_002_4,
        },
        "claude-2.0": {
            "prompt": 0.000_008,
            "completion": 0.000_024,
        },
        "claude-2.1": {
            "prompt": 0.000_008,
            "completion": 0.000_024,
        },
        "claude-3-haiku-20240307": {
            "prompt": 0.000_002_5,
            "completion": 0.000_012_5,
        },
        "claude-3-sonnet-20240229": {
            "prompt": 0.000_003,
            "completion": 0.000_015,
        },
        "claude-3-opus-20240229": {
            "prompt": 0.000_015,
            "completion": 0.000_075,
        },
    }

    try:
        model_pricing = pricing[model]
    except KeyError:
        return None

    prompt_cost = usage.input_tokens * model_pricing["prompt"]
    completion_cost = usage.output_tokens * model_pricing["completion"]
    total_cost = prompt_cost + completion_cost

    return total_cost
