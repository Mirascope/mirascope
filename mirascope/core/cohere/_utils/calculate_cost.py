"""Calculate the cost of a completion using the Cohere API."""

from cohere.types import NonStreamedChatResponse


def calculate_cost(
    response: NonStreamedChatResponse, model="command-r-plus"
) -> float | None:
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
    if not (meta := response.meta) or not (usage := meta.billed_units):
        return None
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
