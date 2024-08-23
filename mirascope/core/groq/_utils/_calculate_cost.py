"""Calculate the cost of a completion using the Groq API."""


def calculate_cost(
    input_tokens: int | float | None,
    output_tokens: int | float | None,
    model: str = "mixtral-8x7b-32768",
) -> float | None:
    """Calculate the cost of a completion using the Groq API.

    https://wow.groq.com/

    Model                                  Input               Output
    llama-3.1-405b-reasoning               N/A                 N/A
    llama-3.1-70b-versatile                N/A                 N/A
    llama-3.1-8b-instant                   N/A                 N/A
    llama3-groq-70b-8192-tool-use-preview  $0.89 / 1M tokens   $0.89 / 1M tokens
    llama3-groq-8b-8192-tool-use-preview   $0.19 / 1M tokens   $0.19 / 1M tokens
    llama3-70b-8192                        $0.59 / 1M tokens   $0.79 / 1M tokens
    llama3-8b-8192                         $0.05 / 1M tokens   $0.08 / 1M tokens
    mixtral-8x7b-32768                     $0.27 / 1M tokens   $0.27 / 1M tokens
    gemma-7b-it                            $0.07 / 1M tokens   $0.07 / 1M tokens
    gemma2-9b-it                           $0.20 / 1M tokens   $0.20 / 1M tokens
    """
    pricing = {
        "llama3-groq-70b-8192-tool-use-preview": {
            "prompt": 0.000_000_89,
            "completion": 0.000_000_89,
        },
        "llama3-groq-8b-8192-tool-use-preview": {
            "prompt": 0.000_000_19,
            "completion": 0.000_000_19,
        },
        "llama3-70b-8192": {
            "prompt": 0.000_000_59,
            "completion": 0.000_000_79,
        },
        "llama3-8b-8192": {
            "prompt": 0.000_000_05,
            "completion": 0.000_000_08,
        },
        "mixtral-8x7b-32768": {
            "prompt": 0.000_000_24,
            "completion": 0.000_000_24,
        },
        "gemma-7b-it": {
            "prompt": 0.000_000_07,
            "completion": 0.000_000_07,
        },
        "gemma2-9b-it": {
            "prompt": 0.000_000_2,
            "completion": 0.000_000_2,
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
