"""Calculate the cost of a Gemini API call."""

from ..base.types import CostMetadata


def calculate_cost(
    metadata: CostMetadata,
    model: str,
) -> float | None:
    """Calculate the cost of a Gemini API call.

    https://ai.google.dev/pricing#1_5flash

    Model                 Input (<=128K)     Output (<=128K)    Input (>128K)      Output (>128K)
    gemini-1.5-flash      $0.075 / 1M        $0.3 / 1M          $0.15 / 1M         $0.6 / 1M
    gemini-1.5-flash-8b   $0.0375 / 1M       $0.15 / 1M         $0.075 / 1M        $0.3 / 1M
    gemini-1.5-pro        $1.25 / 1M         $5.0 / 1M          $2.5 / 1M          $10.0 / 1M
    gemini-1.0-pro        $0.50 / 1M         $1.5 / 1M          $0.5 / 1M          $1.5 / 1M
    """
    pricing = {
        "gemini-1.5-flash": {
            "prompt_short": 0.000_000_075,
            "completion_short": 0.000_000_3,
            "prompt_long": 0.000_000_15,
            "completion_long": 0.000_000_6,
        },
        "gemini-1.5-flash-8b": {
            "prompt_short": 0.000_000_037_5,
            "completion_short": 0.000_000_15,
            "prompt_long": 0.000_000_075,
            "completion_long": 0.000_000_3,
        },
        "gemini-1.5-pro": {
            "prompt_short": 0.000_001_25,
            "completion_short": 0.000_005,
            "prompt_long": 0.000_002_5,
            "completion_long": 0.000_01,
        },
        "gemini-1.0-pro": {
            "prompt_short": 0.000_000_5,
            "completion_short": 0.000_001_5,
            "prompt_long": 0.000_000_5,
            "completion_long": 0.000_001_5,
        },
    }

    if metadata.input_tokens is None or metadata.output_tokens is None:
        return None

    try:
        model_pricing = pricing[model]
    except KeyError:
        return None

    # Determine if we're using long context pricing
    use_long_context = metadata.input_tokens > 128_000

    prompt_price = model_pricing["prompt_long" if use_long_context else "prompt_short"]
    completion_price = model_pricing[
        "completion_long" if use_long_context else "completion_short"
    ]

    prompt_cost = metadata.input_tokens * prompt_price
    completion_cost = metadata.output_tokens * completion_price
    total_cost = prompt_cost + completion_cost

    return total_cost
