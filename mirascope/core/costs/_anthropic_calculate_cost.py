"""Calculate the cost of a completion using the Anthropic API."""

from ..base.types import CostMetadata


def calculate_cost(
    metadata: CostMetadata,
    model: str = "claude-3-haiku-20240229",
) -> float | None:
    """Calculate the cost of a completion using the Anthropic API.

    https://www.anthropic.com/api

    Model                                      Input                 Cached                Output
    claude-3-5-haiku                           $0.80  / 1M tokens    $0.08  / 1M tokens    $4.00  / 1M tokens
    claude-3-5-haiku-20241022                  $0.80  / 1M tokens    $0.08  / 1M tokens    $4.00  / 1M tokens
    claude-3-7-sonnet                          $3.00  / 1M tokens    $0.30  / 1M tokens    $15.00 / 1M tokens
    claude-3-7-sonnet-20250219                 $3.00  / 1M tokens    $0.30  / 1M tokens    $15.00 / 1M tokens
    claude-3-5-sonnet                          $3.00  / 1M tokens    $0.30  / 1M tokens    $15.00 / 1M tokens
    claude-3-5-sonnet-20241022                 $3.00  / 1M tokens    $0.30  / 1M tokens    $15.00 / 1M tokens
    claude-3-5-sonnet-20240620                 $3.00  / 1M tokens    $0.30  / 1M tokens    $15.00 / 1M tokens
    claude-3-haiku                             $0.80  / 1M tokens    $0.08  / 1M tokens    $4.00  / 1M tokens
    claude-3-haiku-20240307                    $0.80  / 1M tokens    $0.08  / 1M tokens    $4.00  / 1M tokens
    claude-3-sonnet                            $3.00  / 1M tokens    $0.30  / 1M tokens    $15.00 / 1M tokens
    claude-3-sonnet-20240620                   $3.00  / 1M tokens    $0.30  / 1M tokens    $15.00 / 1M tokens
    claude-3-opus                              $15.00 / 1M tokens    $1.50  / 1M tokens    $75.00 / 1M tokens
    claude-3-opus-20240229                     $15.00 / 1M tokens    $1.50  / 1M tokens    $75.00 / 1M tokens
    claude-2.1                                 $8.00  / 1M tokens                          $24.00 / 1M tokens
    claude-2.0                                 $8.00  / 1M tokens                          $24.00 / 1M tokens
    claude-instant-1.2                         $0.80  / 1M tokens                          $2.40  / 1M tokens
    anthropic.claude-3-5-sonnet-20241022-v2:0  $3.00  / 1M tokens    $0.30  / 1M tokens    $15.00 / 1M tokens
    anthropic.claude-3-5-sonnet-20241022-v1:0  $3.00  / 1M tokens    $0.30  / 1M tokens    $15.00 / 1M tokens
    anthropic.claude-3-5-haiku-20241022-v1:0   $0.80  / 1M tokens    $0.08  / 1M tokens    $4.00  / 1M tokens
    anthropic.claude-3-sonnet-20240620-v1:0    $3.00  / 1M tokens    $0.30  / 1M tokens    $15.00 / 1M tokens
    anthropic.claude-3-haiku-20240307-v1:0     $0.80  / 1M tokens    $0.08  / 1M tokens    $4.00  / 1M tokens
    anthropic.claude-3-opus-20240229-v1:0      $15.00 / 1M tokens    $1.50  / 1M tokens    $75.00 / 1M tokens
    claude-3-5-sonnet@20241022                 $3.00  / 1M tokens    $0.30  / 1M tokens    $15.00 / 1M tokens
    claude-3-5-haiku@20241022                  $0.80  / 1M tokens    $0.08  / 1M tokens    $4.00  / 1M tokens
    claude-3-sonnet@20240620                   $3.00  / 1M tokens    $0.30  / 1M tokens    $15.00 / 1M tokens
    claude-3-haiku@20240307                    $0.80  / 1M tokens    $0.08  / 1M tokens    $4.00  / 1M tokens
    claude-3-opus@20240229                     $15.00 / 1M tokens    $1.50  / 1M tokens    $75.00 / 1M tokens
    """
    pricing = {
        # Anthropic models
        "claude-3-5-haiku-latest": {
            "prompt": 0.000_000_8,
            "completion": 0.000_004,
            "cached": 0.000_000_08,
        },
        "claude-3-5-haiku-20241022": {
            "prompt": 0.000_000_8,
            "completion": 0.000_004,
            "cached": 0.000_000_08,
        },
        "claude-3-7-sonnet-latest": {
            "prompt": 0.000_003,
            "completion": 0.000_015,
            "cached": 0.000_000_3,
        },
        "claude-3-7-sonnet-20250219": {
            "prompt": 0.000_003,
            "completion": 0.000_015,
            "cached": 0.000_000_3,
        },
        "claude-3-5-sonnet-latest": {
            "prompt": 0.000_003,
            "completion": 0.000_015,
            "cached": 0.000_000_3,
        },
        "claude-3-5-sonnet-20241022": {
            "prompt": 0.000_003,
            "completion": 0.000_015,
            "cached": 0.000_000_3,
        },
        "claude-3-5-sonnet-20240620": {
            "prompt": 0.000_003,
            "completion": 0.000_015,
            "cached": 0.000_000_3,
        },
        "claude-3-haiku-latest": {
            "prompt": 0.000_000_8,
            "completion": 0.000_004,
            "cached": 0.000_000_08,
        },
        "claude-3-haiku-20240307": {
            "prompt": 0.000_000_8,
            "completion": 0.000_004,
            "cached": 0.000_000_08,
        },
        "claude-3-sonnet-latest": {
            "prompt": 0.000_003,
            "completion": 0.000_015,
            "cached": 0.000_000_3,
        },
        "claude-3-sonnet-20240620": {
            "prompt": 0.000_003,
            "completion": 0.000_015,
            "cached": 0.000_000_3,
        },
        "claude-3-opus-latest": {
            "prompt": 0.000_015,
            "completion": 0.000_075,
            "cached": 0.000_001_5,
        },
        "claude-3-opus-20240229": {
            "prompt": 0.000_015,
            "completion": 0.000_075,
            "cached": 0.000_001_5,
        },
        "claude-2.1": {
            "prompt": 0.000_008,
            "completion": 0.000_024,
            "cached": 0,
        },
        "claude-2.0": {
            "prompt": 0.000_008,
            "completion": 0.000_024,
            "cached": 0,
        },
        "claude-instant-1.2": {
            "prompt": 0.000_000_8,
            "completion": 0.000_002_4,
            "cached": 0,
        },
        # Bedrock models
        "anthropic.claude-3-7-sonnet-20250219-v1:0": {
            "prompt": 0.000_003,
            "completion": 0.000_015,
            "cached": 0.000_000_3,
        },
        "anthropic.claude-3-5-sonnet-20241022-v2:0": {
            "prompt": 0.000_003,
            "completion": 0.000_015,
            "cached": 0.000_000_3,
        },
        "anthropic.claude-3-5-sonnet-20241022-v1:0": {
            "prompt": 0.000_003,
            "completion": 0.000_015,
            "cached": 0.000_000_3,
        },
        "anthropic.claude-3-5-haiku-20241022-v1:0": {
            "prompt": 0.000_000_8,
            "completion": 0.000_004,
            "cached": 0.000_000_08,
        },
        "anthropic.claude-3-sonnet-20240620-v1:0": {
            "prompt": 0.000_003,
            "completion": 0.000_015,
            "cached": 0.000_000_3,
        },
        "anthropic.claude-3-haiku-20240307-v1:0": {
            "prompt": 0.000_000_8,
            "completion": 0.000_004,
            "cached": 0.000_000_08,
        },
        "anthropic.claude-3-opus-20240229-v1:0": {
            "prompt": 0.000_015,
            "completion": 0.000_075,
            "cached": 0.000_001_5,
        },
        # Vertex AI models
        "claude-3-7-sonnet@20250219": {
            "prompt": 0.000_003,
            "completion": 0.000_015,
            "cached": 0.000_000_3,
        },
        "claude-3-5-sonnet@20241022": {
            "prompt": 0.000_003,
            "completion": 0.000_015,
            "cached": 0.000_000_3,
        },
        "claude-3-5-haiku@20241022": {
            "prompt": 0.000_000_8,
            "completion": 0.000_004,
            "cached": 0.000_000_08,
        },
        "claude-3-sonnet@20240620": {
            "prompt": 0.000_003,
            "completion": 0.000_015,
            "cached": 0.000_000_3,
        },
        "claude-3-haiku@20240307": {
            "prompt": 0.000_000_8,
            "completion": 0.000_004,
            "cached": 0.000_000_08,
        },
        "claude-3-opus@20240229": {
            "prompt": 0.000_015,
            "completion": 0.000_075,
            "cached": 0.000_001_5,
        },
    }

    if metadata.input_tokens is None or metadata.output_tokens is None:
        return None

    if metadata.cached_tokens is None:
        metadata.cached_tokens = 0

    try:
        model_pricing = pricing[model]
    except KeyError:
        return None

    # Calculate cost for text tokens
    prompt_cost = metadata.input_tokens * model_pricing["prompt"]
    cached_cost = metadata.cached_tokens * model_pricing["cached"]
    completion_cost = metadata.output_tokens * model_pricing["completion"]

    # Image tokens are in response tokens
    # https://docs.anthropic.com/en/docs/build-with-claude/vision#calculate-image-costs

    # PDF documents  tokens are in response tokens
    # https://docs.anthropic.com/en/docs/build-with-claude/pdf-support#estimate-your-costs

    # Sum all costs
    total_cost = prompt_cost + cached_cost + completion_cost

    return total_cost
