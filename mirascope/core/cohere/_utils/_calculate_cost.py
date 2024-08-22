"""Calculate the cost of a completion using the Cohere API."""


def calculate_cost(
    input_tokens: int | float | None,
    output_tokens: int | float | None,
    model: str = "command-r-plus",
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
    if input_tokens is None or output_tokens is None:
        return None

    try:
        model_pricing = pricing[model]
    except KeyError:
        return None

    prompt_cost = input_tokens * model_pricing["prompt"]
    completion_cost = output_tokens * model_pricing["completion"]
    total_cost = prompt_cost + completion_cost

    return total_cost
