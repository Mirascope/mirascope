"""A module for utility functions for working with Anthropic."""

from typing import Callable, Optional, Union

from anthropic import Anthropic, AnthropicBedrock, AsyncAnthropic, AsyncAnthropicBedrock
from anthropic._types import URL
from anthropic.types import Usage


def bedrock_client_wrapper(
    aws_secret_key: Optional[str] = None,
    aws_access_key: Optional[str] = None,
    aws_region: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    base_url: Optional[Union[str, URL]] = None,
) -> Callable[
    [Union[Anthropic, AsyncAnthropic]], Union[AnthropicBedrock, AsyncAnthropicBedrock]
]:
    """Returns a client wrapper for using Anthropic models on AWS Bedrock."""

    def inner_wrapper(client: Union[Anthropic, AsyncAnthropic]):
        """Returns matching `AnthropicBedrock` or `AsyncAnthropicBedrock` client."""
        kwargs = {
            "aws_secret_key": aws_secret_key,
            "aws_access_key": aws_access_key,
            "aws_region": aws_region,
            "aws_session_token": aws_session_token,
            "base_url": base_url,
        }
        if isinstance(client, Anthropic):
            client = AnthropicBedrock(**kwargs)  # type: ignore
        elif isinstance(client, AsyncAnthropic):
            client = AsyncAnthropicBedrock(**kwargs)  # type: ignore
        return client

    return inner_wrapper


def anthropic_api_calculate_cost(
    usage: Usage, model="claude-3-haiku-20240229"
) -> Optional[float]:
    """Calculate the cost of a completion using the Anthropic API.

    https://www.anthropic.com/api

    claude-instant-1.2        $0.80 / 1M tokens   $2.40 / 1M tokens
    claude-2.0                $8.00 / 1M tokens   $24.00 / 1M tokens
    claude-2.1                $8.00 / 1M tokens   $24.00 / 1M tokens
    claude-3-haiku            $0.25 / 1M tokens   $1.25 / 1M tokens
    claude-3-sonnet           $3.00 / 1M tokens   $15.00 / 1M tokens
    claude-3-opus             $15.00 / 1M tokens   $75.00 / 1M tokens
    """
    pricing = {
        "claude-instant-1.2": {
            "prompt": 0.000_000_8,
            "completion": 0.000_002_4,
        },
        "claude-2.0": {
            "prompt": 0.000_008,
            "completion": 0.000_024,
        },
        "claude-2.1": {
            "prompt": 0.000_008,
            "completion": 0.000_024,
        },
        "claude-3-haiku-20240307": {
            "prompt": 0.000_002_5,
            "completion": 0.000_012_5,
        },
        "claude-3-sonnet-20240229": {
            "prompt": 0.000_003,
            "completion": 0.000_015,
        },
        "claude-3-opus-20240229": {
            "prompt": 0.000_015,
            "completion": 0.000_075,
        },
    }

    try:
        model_pricing = pricing[model]
    except KeyError:
        return None

    prompt_cost = usage.input_tokens * model_pricing["prompt"]
    completion_cost = usage.output_tokens * model_pricing["completion"]
    total_cost = prompt_cost + completion_cost

    return total_cost
