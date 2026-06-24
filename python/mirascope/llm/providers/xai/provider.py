"""xAI provider implementation.

Wraps xAI's OpenAI-compatible Responses API (https://api.x.ai/v1) so Grok models
can be used from Mirascope the same way as any other LLM. The class just
specialises `OpenAIResponsesProvider` with xAI's default base URL and a separate
class identity so the provider registry can route `xai/` prefixed model IDs to it.
"""

from __future__ import annotations

import os
from typing import ClassVar

from openai import AsyncOpenAI, OpenAI

from ..openai.responses.provider import OpenAIResponsesProvider

_DEFAULT_XAI_BASE_URL = "https://api.x.ai/v1"
_XAI_API_KEY_ENV_VAR = "XAI_API_KEY"


class XAIProvider(OpenAIResponsesProvider):
    """Provider for xAI's OpenAI-compatible Responses API.

    Inherits everything from `OpenAIResponsesProvider` and only overrides the
    pieces that differ: provider id, default scope, default base URL, and the
    environment variable used to pick up the API key.

    Usage:
        Register the provider for the `xai/` scope, then call Grok models
        directly:

        ```python
        from mirascope import llm

        llm.register_provider("xai")

        @llm.call("xai/grok-2-latest")
        def my_prompt():
            return [llm.messages.user("Hello!")]
        ```
    """

    id: ClassVar[str] = "xai"
    default_scope: ClassVar[str | list[str]] = "xai/"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialize the xAI Responses client.

        Args:
            api_key: xAI API key. Falls back to `XAI_API_KEY` if not provided.
            base_url: Custom base URL. Falls back to `https://api.x.ai/v1`.

        Raises:
            ValueError: If no API key is provided and `XAI_API_KEY` is unset.
        """
        resolved_key = api_key or os.environ.get(_XAI_API_KEY_ENV_VAR)
        if not resolved_key:
            raise ValueError(
                "xAI API key is required. Pass `api_key=...` or set the "
                f"`{_XAI_API_KEY_ENV_VAR}` environment variable."
            )
        resolved_base_url = base_url or _DEFAULT_XAI_BASE_URL
        self.client = OpenAI(api_key=resolved_key, base_url=resolved_base_url)
        self.async_client = AsyncOpenAI(
            api_key=resolved_key, base_url=resolved_base_url
        )
