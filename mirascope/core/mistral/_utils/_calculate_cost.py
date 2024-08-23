"""Calculate the cost of a completion using the Mistral API."""


def calculate_cost(
    input_tokens: int | float | None,
    output_tokens: int | float | None,
    model: str = "open-mistral-7b",
) -> float | None:
    """Calculate the cost of a completion using the Mistral API.

    https://mistral.ai/technology/#pricing

    Model                     Input               Output
    open-mistral-nemo         $0.3/1M tokens	  $0.3/1M tokens
    mistral-large-latest      $3/1M tokens	      $9/1M tokens
    codestral-2405            $1/1M tokens	      $3/1M tokens
    open-mistral-7b	          $0.25/1M tokens	  $0.25/1M tokens
    open-mixtral-8x7b	      $0.7/1M tokens	  $0.7/1M tokens
    open-mixtral-8x22b	      $2/1M tokens	      $6/1M tokens
    mistral-small-latest	  $2/1M tokens	      $6/1M tokens
    mistral-medium-latest     $2.75/1M tokens	  $8.1/1M tokens
    """
    pricing = {
        "open-mistral-nemo": {"prompt": 0.000_000_3, "completion": 0.000_000_3},
        "open-mistral-nemo-2407": {"prompt": 0.000_000_3, "completion": 0.000_000_3},
        "mistral-large-latest": {"prompt": 0.000_003, "completion": 0.000_009},
        "mistral-large-2407": {"prompt": 0.000_003, "completion": 0.000_009},
        "open-mistral-7b": {"prompt": 0.000_000_25, "completion": 0.000_000_25},
        "open-mixtral-8x7b": {"prompt": 0.000_000_7, "completion": 0.000_000_7},
        "open-mixtral-8x22b": {"prompt": 0.000_002, "completion": 0.000_006},
        "mistral-small-latest": {"prompt": 0.000_002, "completion": 0.000_006},
        "mistral-medium-latest": {"prompt": 0.000_002_75, "completion": 0.000_008_1},
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
