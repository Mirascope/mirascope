"""A module for utility functions for working with Groq."""
from typing import Optional

from groq.types.chat.chat_completion import Usage


def groq_api_calculate_cost(
    usage: Usage, model="mixtral-8x7b-32768"
) -> Optional[float]:
    """Calculate the cost of a completion using the Groq API.

    https://wow.groq.com/

    Model                   Input               Output
    llama2-70b-4096         $0.70 / 1M tokens   $0.80 / 1M tokens
    llama2-7b-2048          $0.10 / 1M tokens   $0.10 / 1M tokens
    mixtral-8x7b-32768      $0.27 / 1M tokens   $0.27 / 1M tokens
    gemma-7b-it             $0.10 / 1M tokens   $0.10 / 1M tokens
    """
    pricing = {
        "llama2-70b-4096": {
            "prompt": 0.000_000_7,
            "completion": 0.000_000_8,
        },
        "llama2-7b-2048": {
            "prompt": 0.000_000_1,
            "completion": 0.000_000_1,
        },
        "mixtral-8x7b-32768": {
            "prompt": 0.000_000_27,
            "completion": 0.000_000_27,
        },
        "gemma-7b-it": {
            "prompt": 0.000_000_1,
            "completion": 0.000_000_1,
        },
    }

    try:
        model_pricing = pricing[model]
    except KeyError:
        return None

    prompt_tokens = usage.prompt_tokens or 0
    completion_tokens = usage.completion_tokens or 0
    prompt_cost = prompt_tokens * model_pricing["prompt"]
    completion_cost = completion_tokens * model_pricing["completion"]
    total_cost = prompt_cost + completion_cost

    return total_cost
