"""Calculate the cost of a completion using the Vertex AI Gemini API, considering context window size."""

from ..base.types import CostMetadata


def calculate_cost(
    metadata: CostMetadata,
    model: str = "gemini-1.5-pro",
) -> float | None:
    """Calculate the cost of a completion using the Vertex AI Gemini API.

    https://cloud.google.com/vertex-ai/pricing#generative_ai_models

    Model               Input (<=128K)     Output (<=128K)    Input (>128K)      Output (>128K)
    gemini-1.5-flash    $0.00001875 / 1k   $0.000075 / 1k     $0.0000375 / 1k    $0.00015 / 1k
    gemini-1.5-pro      $0.00125 / 1k      $0.00375 / 1k      $0.0025 / 1k       $0.0075 / 1k
    gemini-1.0-pro      $0.000125 / 1k     $0.000375 / 1k     N/A                N/A

    Note: Prices are per 1k characters. Gemini 1.0 Pro only supports up to 32K context window.
    """

    context_length = metadata.context_length or 0
    pricing = {
        "gemini-1.5-flash": {
            "prompt_short": 0.000_018_75,
            "completion_short": 0.000_075,
            "prompt_long": 0.000_037_5,
            "completion_long": 0.000_15,
        },
        "gemini-1.5-pro": {
            "prompt_short": 0.001_25,
            "completion_short": 0.003_75,
            "prompt_long": 0.002_5,
            "completion_long": 0.007_5,
        },
        "gemini-1.0-pro": {
            "prompt_short": 0.000_125,
            "completion_short": 0.000_375,
            "prompt_long": None,
            "completion_long": None,
        },
    }

    if metadata.input_tokens is None or metadata.output_tokens is None:
        return None

    try:
        model_pricing = pricing[model]
    except KeyError:
        return None

    # Determine if we're using long context pricing
    use_long_context = context_length > 128000

    if use_long_context and model == "gemini-1.0-pro":
        return None  # Gemini 1.0 Pro doesn't support long context

    prompt_price = model_pricing["prompt_long" if use_long_context else "prompt_short"]
    completion_price = model_pricing[
        "completion_long" if use_long_context else "completion_short"
    ]

    prompt_cost = (metadata.input_tokens / 1000) * prompt_price
    completion_cost = (metadata.output_tokens / 1000) * completion_price
    total_cost = prompt_cost + completion_cost

    return total_cost
