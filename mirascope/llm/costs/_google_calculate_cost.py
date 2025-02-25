"""Calculate the cost of a Gemini API call."""


def calculate_cost(
    input_tokens: int | float | None,
    cached_tokens: int | float | None,
    output_tokens: int | float | None,
    model: str,
) -> float | None:
    """Calculate the cost of a Google API call.

    https://ai.google.dev/pricing

    Pricing (per 1M tokens):

    Model                                 Input (<128K)    Output (<128K)   Input (>128K)    Output (>128K)   Cached
    gemini-2.0-pro                        $1.25            $5.00            $2.50            $10.00           $0.625
    gemini-2.0-pro-preview-1206           $1.25            $5.00            $2.50            $10.00           $0.625
    gemini-2.0-flash                      $0.10            $0.40            $0.10            $0.40            $0.0375
    gemini-2.0-flash-latest               $0.10            $0.40            $0.10            $0.40            $0.0375
    gemini-2.0-flash-001                  $0.10            $0.40            $0.10            $0.40            $0.0375
    gemini-2.0-flash-lite                 $0.075           $0.30            $0.075           $0.30            $0.0375
    gemini-2.0-flash-lite-preview-02-05   $0.075           $0.30            $0.075           $0.30            $0.0375
    gemini-1.5-pro                        $1.25            $5.00            $2.50            $10.00           $0.625
    gemini-1.5-pro-latest                 $1.25            $5.00            $2.50            $10.00           $0.625
    gemini-1.5-pro-001                    $1.25            $5.00            $2.50            $10.00           $0.625
    gemini-1.5-pro-002                    $1.25            $5.00            $2.50            $10.00           $0.625
    gemini-1.5-flash                      $0.075           $0.30            $0.15            $0.60            $0.0375
    gemini-1.5-flash-latest               $0.075           $0.30            $0.15            $0.60            $0.0375
    gemini-1.5-flash-001                  $0.075           $0.30            $0.15            $0.60            $0.0375
    gemini-1.5-flash-002                  $0.075           $0.30            $0.15            $0.60            $0.0375
    gemini-1.5-flash-8b                   $0.0375          $0.15            $0.075           $0.30            $0.025
    gemini-1.5-flash-8b-latest            $0.0375          $0.15            $0.075           $0.30            $0.025
    gemini-1.5-flash-8b-001               $0.0375          $0.15            $0.075           $0.30            $0.025
    gemini-1.5-flash-8b-002               $0.0375          $0.15            $0.075           $0.30            $0.025
    gemini-1.0-pro                        $0.50            $1.50            $0.50            $1.50            $0.00

    Args:
        input_tokens: Number of input tokens
        cached_tokens: Number of cached tokens
        output_tokens: Number of output tokens
        model: Model name to use for pricing calculation

    Returns:
        Total cost in USD or None if invalid input
    """
    pricing = {
        "gemini-2.0-pro": {
            "prompt_short": 0.000_001_25,
            "completion_short": 0.000_005,
            "prompt_long": 0.000_002_5,
            "completion_long": 0.000_01,
            "cached": 0.000_000_625,
        },
        "gemini-2.0-pro-preview-1206": {
            "prompt_short": 0.000_001_25,
            "completion_short": 0.000_005,
            "prompt_long": 0.000_002_5,
            "completion_long": 0.000_01,
            "cached": 0.000_000_625,
        },
        "gemini-2.0-flash": {
            "prompt_short": 0.000_000_10,
            "completion_short": 0.000_000_40,
            "prompt_long": 0.000_000_10,
            "completion_long": 0.000_000_40,
            "cached": 0.000_000_037_5,
        },
        "gemini-2.0-flash-latest": {
            "prompt_short": 0.000_000_10,
            "completion_short": 0.000_000_40,
            "prompt_long": 0.000_000_10,
            "completion_long": 0.000_000_40,
            "cached": 0.000_000_037_5,
        },
        "gemini-2.0-flash-001": {
            "prompt_short": 0.000_000_10,
            "completion_short": 0.000_000_40,
            "prompt_long": 0.000_000_10,
            "completion_long": 0.000_000_40,
            "cached": 0.000_000_037_5,
        },
        "gemini-2.0-flash-lite": {
            "prompt_short": 0.000_000_075,
            "completion_short": 0.000_000_30,
            "prompt_long": 0.000_000_075,
            "completion_long": 0.000_000_30,
            "cached": 0.000_000_037_5,
        },
        "gemini-2.0-flash-lite-preview-02-05": {
            "prompt_short": 0.000_000_075,
            "completion_short": 0.000_000_30,
            "prompt_long": 0.000_000_075,
            "completion_long": 0.000_000_30,
            "cached": 0.000_000_037_5,
        },
        "gemini-1.5-pro": {
            "prompt_short": 0.000_001_25,
            "completion_short": 0.000_005,
            "prompt_long": 0.000_002_5,
            "completion_long": 0.000_01,
            "cached": 0.000_000_625,
        },
        "gemini-1.5-pro-latest": {
            "prompt_short": 0.000_001_25,
            "completion_short": 0.000_005,
            "prompt_long": 0.000_002_5,
            "completion_long": 0.000_01,
            "cached": 0.000_000_625,
        },
        "gemini-1.5-pro-001": {
            "prompt_short": 0.000_001_25,
            "completion_short": 0.000_005,
            "prompt_long": 0.000_002_5,
            "completion_long": 0.000_01,
            "cached": 0.000_000_625,
        },
        "gemini-1.5-pro-002": {
            "prompt_short": 0.000_001_25,
            "completion_short": 0.000_005,
            "prompt_long": 0.000_002_5,
            "completion_long": 0.000_01,
            "cached": 0.000_000_625,
        },
        "gemini-1.5-flash": {
            "prompt_short": 0.000_000_075,
            "completion_short": 0.000_000_30,
            "prompt_long": 0.000_000_15,
            "completion_long": 0.000_000_60,
            "cached": 0.000_000_037_5,
        },
        "gemini-1.5-flash-latest": {
            "prompt_short": 0.000_000_075,
            "completion_short": 0.000_000_30,
            "prompt_long": 0.000_000_15,
            "completion_long": 0.000_000_60,
            "cached": 0.000_000_037_5,
        },
        "gemini-1.5-flash-001": {
            "prompt_short": 0.000_000_075,
            "completion_short": 0.000_000_30,
            "prompt_long": 0.000_000_15,
            "completion_long": 0.000_000_60,
            "cached": 0.000_000_037_5,
        },
        "gemini-1.5-flash-002": {
            "prompt_short": 0.000_000_075,
            "completion_short": 0.000_000_30,
            "prompt_long": 0.000_000_15,
            "completion_long": 0.000_000_60,
            "cached": 0.000_000_037_5,
        },
        "gemini-1.5-flash-8b": {
            "prompt_short": 0.000_000_037_5,
            "completion_short": 0.000_000_15,
            "prompt_long": 0.000_000_075,
            "completion_long": 0.000_000_30,
            "cached": 0.000_000_025,
        },
        "gemini-1.5-flash-8b-latest": {
            "prompt_short": 0.000_000_037_5,
            "completion_short": 0.000_000_15,
            "prompt_long": 0.000_000_075,
            "completion_long": 0.000_000_30,
            "cached": 0.000_000_025,
        },
        "gemini-1.5-flash-8b-001": {
            "prompt_short": 0.000_000_037_5,
            "completion_short": 0.000_000_15,
            "prompt_long": 0.000_000_075,
            "completion_long": 0.000_000_30,
            "cached": 0.000_000_025,
        },
        "gemini-1.5-flash-8b-002": {
            "prompt_short": 0.000_000_037_5,
            "completion_short": 0.000_000_15,
            "prompt_long": 0.000_000_075,
            "completion_long": 0.000_000_30,
            "cached": 0.000_000_025,
        },
        "gemini-1.0-pro": {
            "prompt_short": 0.000_000_5,
            "completion_short": 0.000_001_5,
            "prompt_long": 0.000_000_5,
            "completion_long": 0.000_001_5,
            "cached": 0.000_000,
        },
    }

    if input_tokens is None or output_tokens is None:
        return None

    if cached_tokens is None:
        cached_tokens = 0

    try:
        model_pricing = pricing[model]
    except KeyError:
        return None

    # Determine if we're using long context pricing
    use_long_context = input_tokens > 128_000

    prompt_price = model_pricing["prompt_long" if use_long_context else "prompt_short"]
    cached_price = model_pricing["cached"]
    completion_price = model_pricing[
        "completion_long" if use_long_context else "completion_short"
    ]

    prompt_cost = input_tokens * prompt_price
    cached_cost = cached_tokens * cached_price
    completion_cost = output_tokens * completion_price
    total_cost = prompt_cost + cached_cost + completion_cost

    return total_cost
