"""Calculate the cost of a completion using the Cohere API."""

from ..base.types import CostMetadata


def calculate_cost(
    metadata: CostMetadata,
    model: str = "command-r-plus",
) -> float | None:
    """Calculate the cost of a completion using the Cohere API.

    https://cohere.com/pricing

    Model              Input               Cached     Output
    command-r          $0.15 / 1M tokens              $0.6 / 1M tokens
    command-r-plus     $2.5 / 1M tokens               $10 / 1M tokens
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
        "command-r7b-12-2024": {
            "prompt": 0.000_000_375,
            "completion": 0.000_001_5,
        },
    }
    if metadata.input_tokens is None or metadata.output_tokens is None:
        return None

    try:
        model_pricing = pricing[model]
    except KeyError:
        return None

    prompt_cost = metadata.input_tokens * model_pricing["prompt"]
    completion_cost = metadata.output_tokens * model_pricing["completion"]
    total_cost = prompt_cost + completion_cost

    return total_cost
