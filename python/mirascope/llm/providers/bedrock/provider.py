"""Unified Bedrock provider implementation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Literal, cast
from typing_extensions import Unpack

from ...context import Context, DepsT
from ...formatting import Format, FormattableT, OutputParser
from ...messages import Message
from ...responses import (
    AsyncContextResponse,
    AsyncContextStreamResponse,
    AsyncResponse,
    AsyncStreamResponse,
    ContextResponse,
    ContextStreamResponse,
    Response,
    StreamResponse,
)
from ...tools import (
    AsyncContextToolkit,
    AsyncToolkit,
    ContextToolkit,
    Toolkit,
)
from ..anthropic._utils.errors import ANTHROPIC_ERROR_MAP
from ..base import BaseProvider
from . import _utils as bedrock_utils
from .boto3._utils import BEDROCK_BOTO3_ERROR_MAP
from .model_id import BedrockModelId
from .openai import BedrockOpenAIRoutedProvider

if TYPE_CHECKING:
    from anthropic import AnthropicBedrock
    from openai import OpenAI

    from ...models import Params
    from .anthropic import BedrockAnthropicRoutedProvider
    from .boto3 import BedrockBoto3RoutedProvider
    from .boto3.provider import BedrockRuntimeClient
else:
    AnthropicBedrock = None
    OpenAI = None
    BedrockRuntimeClient = None

BEDROCK_ANTHROPIC_MODEL_PREFIXES = tuple(bedrock_utils.default_anthropic_scopes())
BEDROCK_OPENAI_MODEL_PREFIXES = bedrock_utils.BEDROCK_OPENAI_MODEL_PREFIXES

RoutingProviderId = Literal["anthropic", "openai", "boto3"]

BEDROCK_ERROR_MAP: dict[type[Exception], Any] = {
    **ANTHROPIC_ERROR_MAP,
    **BEDROCK_BOTO3_ERROR_MAP,
}


def _default_routing_scopes() -> dict[RoutingProviderId, list[str]]:
    return {
        "anthropic": list(BEDROCK_ANTHROPIC_MODEL_PREFIXES),
        "openai": list(BEDROCK_OPENAI_MODEL_PREFIXES),
        "boto3": [],
    }


def _is_anthropic_arn(model_id: str) -> bool:
    if not model_id.startswith("bedrock/arn:"):
        return False
    if ":bedrock:" not in model_id:
        return False
    return "foundation-model/anthropic." in model_id


class BedrockProvider(
    BaseProvider["AnthropicBedrock | OpenAI | BedrockRuntimeClient | None"]
):
    """Unified provider for Amazon Bedrock using routing.

    Auto-routing matches model IDs to subproviders:
    - Anthropic base model IDs (``bedrock/anthropic.<model>``)
    - Anthropic cross-region inference profile IDs
      (``bedrock/us.anthropic.<model>``, ``bedrock/eu.anthropic.<model>``, etc.)
    - Anthropic foundation model ARNs containing ``foundation-model/anthropic.``
    - OpenAI-compatible model IDs (``bedrock/openai.<model>``)
    - All other ``bedrock/`` model IDs route to the boto3 Converse API

    You can add custom routing prefixes via ``routing_scopes`` to override the
    default routing behavior.
    """

    id = "bedrock"
    default_scope = "bedrock/"
    error_map = BEDROCK_ERROR_MAP

    def __init__(
        self,
        *,
        aws_region: str | None = None,
        aws_access_key: str | None = None,
        aws_secret_key: str | None = None,
        aws_session_token: str | None = None,
        aws_profile: str | None = None,
        base_url: str | None = None,
        routing_scopes: dict[RoutingProviderId, list[str]] | None = None,
        anthropic_api_key: str | None = None,
        openai_api_key: str | None = None,
    ) -> None:
        """Initialize the Bedrock provider.

        Args:
            aws_region: AWS region for Bedrock. Defaults to environment configuration.
            aws_access_key: AWS access key ID. Defaults to environment configuration.
            aws_secret_key: AWS secret access key. Defaults to environment configuration.
            aws_session_token: AWS session token for temporary credentials.
            aws_profile: AWS profile name for credentials. Defaults to environment.
            base_url: Custom base URL for Bedrock endpoint (e.g., for GovCloud).
            routing_scopes: Optional mapping of provider ids to additional
                model-id prefixes (for example, ``"bedrock/my-custom-model"``) used
                for routing. These prefixes extend the defaults (Anthropic and OpenAI
                prefixes), and routing selects the longest matching prefix. Model IDs
                with the ``bedrock/`` prefix that don't match any routing scope fall
                back to the boto3 Converse API. Model IDs without the ``bedrock/``
                prefix raise ``ValueError``.
            anthropic_api_key: Optional API key for Anthropic subprovider authentication.
                If provided, this takes priority over AWS credentials for Anthropic models.
            openai_api_key: Optional API key for OpenAI subprovider authentication.
                If provided, this takes priority over AWS credentials for OpenAI models.
        """
        self._anthropic_provider: BedrockAnthropicRoutedProvider | None = None
        self._openai_provider: BedrockOpenAIRoutedProvider | None = None
        self._boto3_provider: BedrockBoto3RoutedProvider | None = None
        self.client: AnthropicBedrock | OpenAI | BedrockRuntimeClient | None = None
        self._aws_region = aws_region
        self._aws_access_key = aws_access_key
        self._aws_secret_key = aws_secret_key
        self._aws_session_token = aws_session_token
        self._aws_profile = aws_profile
        self._base_url = base_url
        self._anthropic_api_key = anthropic_api_key
        self._openai_api_key = openai_api_key
        self._routing_scopes = _default_routing_scopes()
        if routing_scopes:
            for provider_id, scopes in routing_scopes.items():
                self._routing_scopes[provider_id].extend(scopes)

    def _get_anthropic_provider(self) -> BedrockAnthropicRoutedProvider:
        if self._anthropic_provider is None:
            from .anthropic import BedrockAnthropicRoutedProvider

            self._anthropic_provider = BedrockAnthropicRoutedProvider(
                api_key=self._anthropic_api_key,
                aws_region=self._aws_region,
                aws_access_key=self._aws_access_key,
                aws_secret_key=self._aws_secret_key,
                aws_session_token=self._aws_session_token,
                aws_profile=self._aws_profile,
                base_url=self._base_url,
            )
            self.client = self._anthropic_provider.client
        return self._anthropic_provider

    def _get_openai_provider(self) -> BedrockOpenAIRoutedProvider:
        if self._openai_provider is None:
            self._openai_provider = BedrockOpenAIRoutedProvider(
                api_key=self._openai_api_key,
                aws_region=self._aws_region,
                aws_access_key_id=self._aws_access_key,
                aws_secret_access_key=self._aws_secret_key,
                aws_session_token=self._aws_session_token,
                aws_profile=self._aws_profile,
                base_url=self._base_url,
            )
            self.client = self._openai_provider.client
        return self._openai_provider

    def _get_boto3_provider(self) -> BedrockBoto3RoutedProvider:
        if self._boto3_provider is None:
            from importlib import import_module

            bedrock_boto3 = import_module("mirascope.llm.providers.bedrock.boto3")
            BedrockBoto3RoutedProvider = cast(
                type["BedrockBoto3RoutedProvider"],
                bedrock_boto3.BedrockBoto3RoutedProvider,
            )

            self._boto3_provider = BedrockBoto3RoutedProvider(
                aws_region=self._aws_region,
                aws_access_key=self._aws_access_key,
                aws_secret_key=self._aws_secret_key,
                aws_session_token=self._aws_session_token,
                aws_profile=self._aws_profile,
                base_url=self._base_url,
            )
        provider = self._boto3_provider
        self.client = provider.client
        return provider

    def get_error_status(self, e: Exception) -> int | None:
        """Extract HTTP status code from provider exception."""
        return getattr(e, "status_code", None)

    def _choose_subprovider(
        self, model_id: BedrockModelId, messages: Sequence[Message]
    ) -> (
        BedrockAnthropicRoutedProvider
        | BedrockOpenAIRoutedProvider
        | BedrockBoto3RoutedProvider
    ):
        route = self._route_provider(model_id)
        if route == "anthropic":
            return self._get_anthropic_provider()
        if route == "openai":
            return self._get_openai_provider()
        if route == "boto3":
            return self._get_boto3_provider()

        # Fall back to boto3 for all other model IDs with bedrock/ prefix
        if model_id.startswith("bedrock/"):
            return self._get_boto3_provider()

        raise ValueError(
            f"Unable to route model '{model_id}' to a Bedrock subprovider. "
            f"Model ID must start with 'bedrock/' prefix."
        )

    def _route_provider(self, model_id: BedrockModelId) -> RoutingProviderId | None:
        # Special case: check for Anthropic ARNs
        if _is_anthropic_arn(model_id):
            return "anthropic"

        best_match: tuple[RoutingProviderId, int] | None = None
        for provider_id, scopes in self._routing_scopes.items():
            for scope in scopes:
                if model_id.startswith(scope):
                    match = (provider_id, len(scope))
                    if best_match is None or match[1] > best_match[1]:
                        best_match = match
        if best_match is None:
            return None
        return best_match[0]

    def _call(
        self,
        *,
        model_id: BedrockModelId,
        messages: Sequence[Message],
        toolkit: Toolkit,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` by synchronously calling the Bedrock API.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters. See `llm.Params`.

        Returns:
            An `llm.Response` object containing the LLM-generated content.
        """
        client = self._choose_subprovider(model_id, messages)
        return client.call(
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            **params,
        )

    def _context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: BedrockModelId,
        messages: Sequence[Message],
        toolkit: ContextToolkit[DepsT],
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextResponse` by synchronously calling the Bedrock API.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters. See `llm.Params`.

        Returns:
            An `llm.ContextResponse` object containing the LLM-generated content.
        """
        client = self._choose_subprovider(model_id, messages)
        return client.context_call(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            **params,
        )

    async def _call_async(
        self,
        *,
        model_id: BedrockModelId,
        messages: Sequence[Message],
        toolkit: AsyncToolkit,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` by calling the Bedrock API asynchronously.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters. See `llm.Params`.

        Returns:
            An `llm.AsyncResponse` object containing the LLM-generated content.
        """
        client = self._choose_subprovider(model_id, messages)
        return await client.call_async(
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            **params,
        )

    async def _context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: BedrockModelId,
        messages: Sequence[Message],
        toolkit: AsyncContextToolkit[DepsT],
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate an `llm.AsyncContextResponse` by calling the Bedrock API asynchronously.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters. See `llm.Params`.

        Returns:
            An `llm.AsyncContextResponse` object containing the LLM-generated content.
        """
        client = self._choose_subprovider(model_id, messages)
        return await client.context_call_async(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            **params,
        )

    def _stream(
        self,
        *,
        model_id: BedrockModelId,
        messages: Sequence[Message],
        toolkit: Toolkit,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Generate an `llm.StreamResponse` by streaming the Bedrock API response.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters. See `llm.Params`.

        Returns:
            An `llm.StreamResponse` for streaming the LLM-generated content.
        """
        client = self._choose_subprovider(model_id, messages)
        return client.stream(
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            **params,
        )

    def _context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: BedrockModelId,
        messages: Sequence[Message],
        toolkit: ContextToolkit[DepsT],
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextStreamResponse` by streaming the Bedrock API response.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters. See `llm.Params`.

        Returns:
            An `llm.ContextStreamResponse` for streaming the LLM-generated content.
        """
        client = self._choose_subprovider(model_id, messages)
        return client.context_stream(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            **params,
        )

    async def _stream_async(
        self,
        *,
        model_id: BedrockModelId,
        messages: Sequence[Message],
        toolkit: AsyncToolkit,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Generate an `llm.AsyncStreamResponse` by streaming the Bedrock API response.

        Args:
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters. See `llm.Params`.

        Returns:
            An `llm.AsyncStreamResponse` for streaming the LLM-generated content.
        """
        client = self._choose_subprovider(model_id, messages)
        return await client.stream_async(
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            **params,
        )

    async def _context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: BedrockModelId,
        messages: Sequence[Message],
        toolkit: AsyncContextToolkit[DepsT],
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> (
        AsyncContextStreamResponse[DepsT]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Generate an `llm.AsyncContextStreamResponse` by streaming the Bedrock API response.

        Args:
            ctx: Context object with dependencies for tools.
            model_id: Model identifier to use.
            messages: Messages to send to the LLM.
            tools: Optional tools that the model may invoke.
            format: Optional response format specifier.
            **params: Additional parameters. See `llm.Params`.

        Returns:
            An `llm.AsyncContextStreamResponse` for streaming the LLM-generated content.
        """
        client = self._choose_subprovider(model_id, messages)
        return await client.context_stream_async(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            **params,
        )
