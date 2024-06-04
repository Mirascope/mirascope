"""A module for utility functions for working with OpenAI."""

from typing import Callable, Optional, Union

from openai import AsyncAzureOpenAI, AsyncOpenAI, AzureOpenAI, OpenAI
from openai.lib.azure import AsyncAzureADTokenProvider, AzureADTokenProvider
from openai.types.completion_usage import CompletionUsage


def azure_client_wrapper(
    azure_endpoint: str,
    azure_deployment: Optional[str] = None,
    api_version: Optional[str] = None,
    api_key: Optional[str] = None,
    azure_ad_token: Optional[str] = None,
    azure_ad_token_provider: Optional[
        Union[AzureADTokenProvider, AsyncAzureADTokenProvider]
    ] = None,
    organization: Optional[str] = None,
) -> Callable[[Union[OpenAI, AsyncOpenAI]], Union[AzureOpenAI, AsyncAzureOpenAI]]:
    """Returns a client wrapper for using OpenAI models on Microsoft Azure."""

    def inner_azure_client_wrapper(client: Union[OpenAI, AsyncOpenAI]):
        """Returns matching `AzureOpenAI` or `AsyncAzureOpenAI` client."""
        kwargs = {
            "azure_endpoint": azure_endpoint,
            "azure_deployment": azure_deployment,
            "api_version": api_version,
            "api_key": api_key,
            "azure_ad_token": azure_ad_token,
            "azure_ad_token_provider": azure_ad_token_provider,
            "organization": organization,
        }
        if isinstance(client, OpenAI):
            client = AzureOpenAI(**kwargs)  # type: ignore
        elif isinstance(client, AsyncOpenAI):
            client = AsyncAzureOpenAI(**kwargs)  # type: ignore
        return client

    return inner_azure_client_wrapper


def openai_api_calculate_cost(
    usage: Optional[CompletionUsage], model="gpt-3.5-turbo-16k"
) -> Optional[float]:
    """Calculate the cost of a completion using the OpenAI API.

    https://openai.com/pricing

    Model                   Input               Output
    gpt-4o                  $5.00 / 1M tokens   $15.00 / 1M tokens
    gpt-4o-2024-05-13       $5.00 / 1M tokens   $15.00 / 1M tokens
    gpt-4-turbo             $10.00 / 1M tokens  $30.00 / 1M tokens
    gpt-4-turbo-2024-04-09  $10.00 / 1M tokens  $30.00 / 1M tokens
    gpt-3.5-turbo-0125	    $0.50 / 1M tokens	$1.50 / 1M tokens
    gpt-3.5-turbo-1106	    $1.00 / 1M tokens	$2.00 / 1M tokens
    gpt-4-1106-preview	    $10.00 / 1M tokens 	$30.00 / 1M tokens
    gpt-4	                $30.00 / 1M tokens	$60.00 / 1M tokens
    text-embedding-3-small	$0.02 / 1M tokens
    text-embedding-3-large	$0.13 / 1M tokens
    text-embedding-ada-0002	$0.10 / 1M tokens
    """
    pricing = {
        "gpt-4o": {
            "prompt": 0.000_005,
            "completion": 0.000_015,
        },
        "gpt-4o-2024-05-13": {
            "prompt": 0.000_005,
            "completion": 0.000_015,
        },
        "gpt-4-turbo": {
            "prompt": 0.000_01,
            "completion": 0.000_03,
        },
        "gpt-4-turbo-2024-04-09": {
            "prompt": 0.000_01,
            "completion": 0.000_03,
        },
        "gpt-3.5-turbo-0125": {
            "prompt": 0.000_000_5,
            "completion": 0.000_001_5,
        },
        "gpt-3.5-turbo-1106": {
            "prompt": 0.000_001,
            "completion": 0.000_002,
        },
        "gpt-4-1106-preview": {
            "prompt": 0.000_01,
            "completion": 0.000_03,
        },
        "gpt-4": {
            "prompt": 0.000_003,
            "completion": 0.000_006,
        },
        "gpt-3.5-turbo-4k": {
            "prompt": 0.000_015,
            "completion": 0.000_02,
        },
        "gpt-3.5-turbo-16k": {
            "prompt": 0.000_003,
            "completion": 0.000_004,
        },
        "gpt-4-8k": {
            "prompt": 0.000_003,
            "completion": 0.000_006,
        },
        "gpt-4-32k": {
            "prompt": 0.000_006,
            "completion": 0.000_012,
        },
        "text-embedding-3-small": {
            "prompt": 0.000_000_02,
            "completion": 0.000_000_02,
        },
        "text-embedding-ada-002": {
            "prompt": 0.000_000_1,
            "completion": 0.000_000_1,
        },
        "text-embedding-3-large": {
            "prompt": 0.000_000_13,
            "completion": 0.000_000_13,
        },
    }
    if usage is None:
        return None
    try:
        model_pricing = pricing[model]
    except KeyError:
        return None

    prompt_cost = usage.prompt_tokens * model_pricing["prompt"]
    completion_cost = usage.completion_tokens * model_pricing["completion"]
    total_cost = prompt_cost + completion_cost

    return total_cost
