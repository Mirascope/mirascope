"""Unified Bedrock provider implementation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Literal
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
    AsyncContextTool,
    AsyncContextToolkit,
    AsyncTool,
    AsyncToolkit,
    ContextTool,
    ContextToolkit,
    Tool,
    Toolkit,
)
from ..anthropic._utils.errors import ANTHROPIC_ERROR_MAP
from ..base import BaseProvider
from . import _utils as bedrock_utils
from .model_id import BedrockModelId

if TYPE_CHECKING:
    from anthropic import AnthropicBedrock

    from ...models import Params
    from .anthropic import BedrockAnthropicRoutedProvider
else:
    AnthropicBedrock = None

BEDROCK_ANTHROPIC_MODEL_PREFIXES = tuple(bedrock_utils.default_anthropic_scopes())

RoutingProviderId = Literal["anthropic"]


def _default_routing_scopes() -> dict[RoutingProviderId, list[str]]:
    return {
        "anthropic": list(BEDROCK_ANTHROPIC_MODEL_PREFIXES),
    }


def _is_anthropic_arn(model_id: str) -> bool:
    if not model_id.startswith("bedrock/arn:"):
        return False
    if ":bedrock:" not in model_id:
        return False
    return "foundation-model/anthropic." in model_id


class BedrockProvider(BaseProvider["AnthropicBedrock | None"]):
    """Unified provider for Amazon Bedrock using routing.

    Auto-routing is strict. It matches only:
    - Anthropic base model IDs (``bedrock/anthropic.<model>``)
    - Anthropic cross-region inference profile IDs
      (``bedrock/us.anthropic.<model>``, ``bedrock/eu.anthropic.<model>``, etc.)
    - Anthropic foundation model ARNs containing ``foundation-model/anthropic.``

    Other model identifiers (OpenAI-compatible, Converse, InvokeModel) are not
    auto-detected in this initial implementation. If a model id does not match
    one of the defaults above, you must add routing prefixes via
    ``routing_scopes``; otherwise calling this provider raises ``ValueError``
    with guidance on how to configure routing.
    """

    id = "bedrock"
    default_scope = "bedrock/"
    error_map = ANTHROPIC_ERROR_MAP

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
                for routing. These prefixes extend the defaults (Anthropic prefixes),
                and routing selects the longest matching prefix. If no prefix matches
                a model id at call time, this provider raises ``ValueError`` with
                guidance on how to configure routing.
            anthropic_api_key: Optional API key for Anthropic subprovider authentication.
                If provided, this takes priority over AWS credentials for Anthropic models.
        """
        self._anthropic_provider: BedrockAnthropicRoutedProvider | None = None
        self.client: Any = None
        self._aws_region = aws_region
        self._aws_access_key = aws_access_key
        self._aws_secret_key = aws_secret_key
        self._aws_session_token = aws_session_token
        self._aws_profile = aws_profile
        self._base_url = base_url
        self._anthropic_api_key = anthropic_api_key
        self._routing_scopes = _default_routing_scopes()
        if routing_scopes:
            for provider_id, scopes in routing_scopes.items():
                self._routing_scopes[provider_id].extend(scopes)

    def _get_anthropic_provider(self) -> BedrockAnthropicRoutedProvider:
        if self._anthropic_provider is None:
            try:
                from .anthropic import BedrockAnthropicRoutedProvider
            except ImportError:
                from ...._stubs import make_import_error

                raise make_import_error(
                    "anthropic", "BedrockAnthropicProvider"
                ) from None

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

    def get_error_status(self, e: Exception) -> int | None:
        """Extract HTTP status code from provider exception."""
        return getattr(e, "status_code", None)

    def _choose_subprovider(
        self, model_id: BedrockModelId, messages: Sequence[Message]
    ) -> BedrockAnthropicRoutedProvider:
        route = self._route_provider(model_id)
        if route == "anthropic":
            return self._get_anthropic_provider()

        message = (
            "BedrockProvider could not determine which SDK to use for "
            f"model_id='{model_id}'. Auto-routing only supports Anthropic model "
            "prefixes (e.g., 'bedrock/anthropic.', 'bedrock/us.anthropic.', or "
            "Anthropic foundation model ARNs). If you need to use a different model, "
            "pass routing_scopes={'anthropic': ['bedrock/<prefix>']} when "
            "registering the BedrockProvider."
        )
        raise ValueError(message)

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
        tools: Sequence[Tool] | Toolkit | None = None,
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
            tools=tools,
            format=format,
            **params,
        )

    def _context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: BedrockModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
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
            tools=tools,
            format=format,
            **params,
        )

    async def _call_async(
        self,
        *,
        model_id: BedrockModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
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
            tools=tools,
            format=format,
            **params,
        )

    async def _context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: BedrockModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
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
            tools=tools,
            format=format,
            **params,
        )

    def _stream(
        self,
        *,
        model_id: BedrockModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool] | Toolkit | None = None,
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
            tools=tools,
            format=format,
            **params,
        )

    def _context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: BedrockModelId,
        messages: Sequence[Message],
        tools: Sequence[Tool | ContextTool[DepsT]]
        | ContextToolkit[DepsT]
        | None = None,
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
            tools=tools,
            format=format,
            **params,
        )

    async def _stream_async(
        self,
        *,
        model_id: BedrockModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool] | AsyncToolkit | None = None,
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
            tools=tools,
            format=format,
            **params,
        )

    async def _context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: BedrockModelId,
        messages: Sequence[Message],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]]
        | AsyncContextToolkit[DepsT]
        | None = None,
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
            tools=tools,
            format=format,
            **params,
        )
