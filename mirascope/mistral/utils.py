"""A module for utility functions for working with Mistral."""

from typing import Optional

from mistralai.models.chat_completion import UsageInfo


def mistral_api_calculate_cost(
    usage: UsageInfo, model="open-mistral-7b"
) -> Optional[float]:
    """Calculate the cost of a completion using the Mistral API.

    https://mistral.ai/technology/#pricing

    Model                     Input               Output
    open-mistral-7b	          $0.25/1M tokens	  $0.25/1M tokens
    open-mixtral-8x7b	      $0.7/1M tokens	  $0.7/1M tokens
    open-mixtral-8x22b	      $2/1M tokens	      $6/1M tokens
    mistral-small		      $2/1M tokens	      $6/1M tokens
    mistral-medium		      $2.7/1M tokens	  $8.1/1M tokens
    mistral-large		      $8/1M tokens	      $24/1M tokens
    """
    pricing = {
        "open-mistral-7b": {"prompt": 0.000_000_25, "completion": 0.000_000_25},
        "open-mixtral-8x7b": {"prompt": 0.000_000_7, "completion": 0.000_000_7},
        "open-mixtral-8x22b": {"prompt": 0.000_002, "completion": 0.000_006},
        "mistral-small": {"prompt": 0.000_002, "completion": 0.000_006},
        "mistral-medium": {"prompt": 0.000_002_7, "completion": 0.000_008_1},
        "mistral-large": {"prompt": 0.000_008, "completion": 0.000_024},
    }

    try:
        model_pricing = pricing[model]
    except KeyError:
        return None

    completion_tokens = usage.completion_tokens or 0
    prompt_cost = usage.prompt_tokens * model_pricing["prompt"]
    completion_cost = completion_tokens * model_pricing["completion"]
    total_cost = prompt_cost + completion_cost

    return total_cost
