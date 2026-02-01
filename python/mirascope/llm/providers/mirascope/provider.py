"""Mirascope Router provider that routes requests through the Mirascope Router API."""

from __future__ import annotations

import os
from collections.abc import Sequence
from typing import TYPE_CHECKING
from typing_extensions import Unpack

from ...context import Context, DepsT
from ...formatting import FormatSpec, FormattableT
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
from ..base import BaseProvider, Provider
from . import _utils

if TYPE_CHECKING:
    from ...models import Params


class MirascopeProvider(BaseProvider[None]):
    """Provider that routes LLM requests through the Mirascope Router API.

    The Mirascope Router provides a unified API for multiple LLM providers
    (Anthropic, Google, OpenAI) with usage tracking and cost calculation.

    This provider:
    - Takes model IDs in the format "scope/model-name" (e.g., "openai/gpt-4")
    - Routes requests to the Mirascope Router endpoint
    - Delegates to the appropriate underlying provider (Anthropic, Google, or OpenAI)
    - Uses MIRASCOPE_API_KEY for authentication

    Environment Variables:
        MIRASCOPE_API_KEY: Required API key for Mirascope Router authentication
        MIRASCOPE_ROUTER_BASE_URL: Optional base URL override
            (default: https://mirascope.com/router/v2)

    Example:
        ```python
        import os
        from mirascope import llm

        os.environ["MIRASCOPE_API_KEY"] = "mk..."

        # Register the Mirascope provider
        llm.register_provider(
            "mirascope",
            scope=["anthropic/", "google/", "openai/"],
        )

        # Use with llm.call decorator
        @llm.call("openai/gpt-4")
        def recommend_book(genre: str):
            return f"Recommend a {genre} book"

        response = recommend_book("fantasy")
        print(response.content)
        ```
    """

    id = "mirascope"
    default_scope = ["anthropic/", "google/", "openai/"]
    error_map = {}
    """Empty error map since MirascopeProvider delegates to underlying providers.

    Error handling is performed by the underlying provider instances (Anthropic,
    Google, OpenAI), which have their own error maps. Any exceptions that bubble
    up from underlying providers are already converted to Mirascope exceptions.
    """

    def __init__(
        self, *, api_key: str | None = None, base_url: str | None = None
    ) -> None:
        """Initialize the Mirascope provider.

        Args:
            api_key: Mirascope API key. If not provided, reads from MIRASCOPE_API_KEY
                environment variable.
            base_url: Optional base URL override for the Mirascope Router. If not
                provided, reads from MIRASCOPE_ROUTER_BASE_URL environment variable
                or defaults to https://mirascope.com/router/v2
        """
        api_key = api_key or os.environ.get("MIRASCOPE_API_KEY")
        if not api_key:
            raise ValueError(
                "Mirascope API key not found. "
                "Set MIRASCOPE_API_KEY environment variable or pass api_key parameter."
            )

        self.api_key = api_key
        self.router_base_url = base_url or _utils.get_default_router_base_url()
        self.client = None  # No single client; we create per-provider clients

    def get_error_status(self, e: Exception) -> int | None:
        """Extract HTTP status code from exception.

        Since MirascopeProvider delegates to underlying providers, this method
        is not used for direct error extraction. Underlying providers handle
        their own status code extraction.

        Args:
            e: The exception to extract status code from.

        Returns:
            None, as status extraction is handled by underlying providers.
        """
        return None

    def _get_underlying_provider(self, model_id: str) -> Provider:
        """Get the underlying provider for a model ID.

        Args:
            model_id: Model identifier in format "scope/model-name"

        Returns:
            The appropriate cached provider instance (Anthropic, Google, or OpenAI)

        Raises:
            ValueError: If the model ID format is invalid or provider is unsupported
        """
        model_scope = _utils.extract_model_scope(model_id)
        if not model_scope:
            raise ValueError(
                f"Invalid model ID format: {model_id}. "
                f"Expected format 'scope/model-name' (e.g., 'openai/gpt-4')"
            )

        # Use the cached function to get/create the provider
        return _utils.create_underlying_provider(
            model_scope=model_scope,
            api_key=self.api_key,
            router_base_url=self.router_base_url,
        )

    def _call(
        self,
        *,
        model_id: str,
        messages: Sequence[Message],
        toolkit: Toolkit,
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        """Generate an `llm.Response` by calling through the Mirascope Router."""
        provider = self._get_underlying_provider(model_id)
        return provider.call(
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
        model_id: str,
        messages: Sequence[Message],
        toolkit: ContextToolkit[DepsT],
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        """Generate an `llm.ContextResponse` by calling through the Mirascope Router."""
        provider = self._get_underlying_provider(model_id)
        return provider.context_call(
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
        model_id: str,
        messages: Sequence[Message],
        toolkit: AsyncToolkit,
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        """Generate an `llm.AsyncResponse` by calling through the Mirascope Router."""
        provider = self._get_underlying_provider(model_id)
        return await provider.call_async(
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
        model_id: str,
        messages: Sequence[Message],
        toolkit: AsyncContextToolkit[DepsT],
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        """Generate an `llm.AsyncContextResponse` by calling through the Mirascope Router."""
        provider = self._get_underlying_provider(model_id)
        return await provider.context_call_async(
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
        model_id: str,
        messages: Sequence[Message],
        toolkit: Toolkit,
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        """Stream an `llm.StreamResponse` by calling through the Mirascope Router."""
        provider = self._get_underlying_provider(model_id)
        return provider.stream(
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
        model_id: str,
        messages: Sequence[Message],
        toolkit: ContextToolkit[DepsT],
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> (
        ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormattableT]
    ):
        """Stream an `llm.ContextStreamResponse` by calling through the Mirascope Router."""
        provider = self._get_underlying_provider(model_id)
        return provider.context_stream(
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
        model_id: str,
        messages: Sequence[Message],
        toolkit: AsyncToolkit,
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        """Stream an `llm.AsyncStreamResponse` by calling through the Mirascope Router."""
        provider = self._get_underlying_provider(model_id)
        return await provider.stream_async(
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
        model_id: str,
        messages: Sequence[Message],
        toolkit: AsyncContextToolkit[DepsT],
        format: FormatSpec[FormattableT] | None = None,
        **params: Unpack[Params],
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        """Stream an `llm.AsyncContextStreamResponse` by calling through the Mirascope Router."""
        provider = self._get_underlying_provider(model_id)
        return await provider.context_stream_async(
            ctx=ctx,
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            **params,
        )
