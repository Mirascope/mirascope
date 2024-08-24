"""OpenAI modules for the v0 look-alike implementation."""

from collections.abc import Callable
from typing import ClassVar, Generic, TypeVar

from openai import AsyncAzureOpenAI, AsyncOpenAI, AzureOpenAI, OpenAI
from openai.lib.azure import AsyncAzureADTokenProvider, AzureADTokenProvider
from openai.types.chat import ChatCompletionToolChoiceOptionParam
from openai.types.chat.completion_create_params import ResponseFormat
from pydantic import ConfigDict

from ..core.openai import (
    OpenAICallResponse,
    OpenAICallResponseChunk,
    OpenAITool,
    openai_call,
)
from .base import BaseCall, BaseCallParams, BaseExtractor, ExtractedType


def azure_client_wrapper(
    azure_endpoint: str,
    azure_deployment: str | None = None,
    api_version: str | None = None,
    api_key: str | None = None,
    azure_ad_token: str | None = None,
    azure_ad_token_provider: AzureADTokenProvider
    | AsyncAzureADTokenProvider
    | None = None,
    organization: str | None = None,
) -> Callable[[OpenAI | AsyncOpenAI], AzureOpenAI | AsyncAzureOpenAI]:
    """Returns a client wrapper for using OpenAI models on Microsoft Azure."""

    def inner_azure_client_wrapper(
        client: OpenAI | AsyncOpenAI,
    ) -> AzureOpenAI | AsyncAzureOpenAI:
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
            return AzureOpenAI(**kwargs)
        return AsyncAzureOpenAI(**kwargs)

    return inner_azure_client_wrapper


class OpenAICallParams(BaseCallParams):
    """The parameters to use when calling the OpenAI API."""

    model: str
    frequency_penalty: float | None = None
    logit_bias: dict[str, int] | None = None
    logprobs: bool | None = None
    max_tokens: int | None = None
    n: int | None = None
    presence_penalty: float | None = None
    response_format: ResponseFormat | None = None
    seed: int | None = None
    stop: str | list[str] | None = None
    temperature: float | None = None
    tool_choice: ChatCompletionToolChoiceOptionParam | None = None
    top_logprobs: int | None = None
    top_p: float | None = None
    user: str | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")


class OpenAICall(BaseCall[OpenAICallResponse, OpenAICallResponseChunk, OpenAITool]):
    call_params: ClassVar[BaseCallParams] = OpenAICallParams(model="gpt-4o-mini")

    _decorator = openai_call
    _provider = "openai"


T = TypeVar("T", bound=ExtractedType)


class OpenAIExtractor(BaseExtractor[T], Generic[T]):
    call_params: ClassVar[BaseCallParams] = OpenAICallParams(model="gpt-4o-mini")

    _decorator = openai_call
    _provider = "openai"
