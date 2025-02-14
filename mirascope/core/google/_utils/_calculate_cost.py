def calculate_cost(
    input_tokens: int | float | None, output_tokens: int | float | None, model: str
) -> float | None:
    """Calculate the cost of a Google API call.

    Pricing (per 1M tokens):

    Model                   Input (<128K)    Output (<128K)    Input (>128K)    Output (>128K)
    gemini-2.0-flash       $0.10            $0.40            $0.10            $0.40
    gemini-2.0-flash-lite  $0.075           $0.30            $0.075           $0.30
    gemini-1.5-flash       $0.075           $0.30            $0.15            $0.60
    gemini-1.5-flash-8b    $0.0375          $0.15            $0.075           $0.30
    gemini-1.5-pro         $1.25            $5.00            $2.50            $10.00
    gemini-1.0-pro         $0.50            $1.50            $0.50            $1.50

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model name to use for pricing calculation

    Returns:
        Total cost in USD or None if invalid input
    """
    pricing = {
        "gemini-2.0-flash": {
            "prompt_short": 0.000_000_10,
            "completion_short": 0.000_000_40,
            "prompt_long": 0.000_000_10,
            "completion_long": 0.000_000_40,
        },
        "gemini-2.0-flash-lite": {
            "prompt_short": 0.000_000_075,
            "completion_short": 0.000_000_30,
            "prompt_long": 0.000_000_075,
            "completion_long": 0.000_000_30,
        },
        "gemini-1.5-flash": {
            "prompt_short": 0.000_000_075,
            "completion_short": 0.000_000_30,
            "prompt_long": 0.000_000_15,
            "completion_long": 0.000_000_60,
        },
        "gemini-1.5-flash-8b": {
            "prompt_short": 0.000_000_037_5,
            "completion_short": 0.000_000_15,
            "prompt_long": 0.000_000_075,
            "completion_long": 0.000_000_30,
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

    if input_tokens is None or output_tokens is None:
        return None

    try:
        model_pricing = pricing[model]
    except KeyError:
        return None

    # Determine if we're using long context pricing
    use_long_context = input_tokens > 128_000

    prompt_price = model_pricing["prompt_long" if use_long_context else "prompt_short"]
    completion_price = model_pricing[
        "completion_long" if use_long_context else "completion_short"
    ]

    prompt_cost = input_tokens * prompt_price
    completion_cost = output_tokens * completion_price
    total_cost = prompt_cost + completion_cost

    return total_cost
