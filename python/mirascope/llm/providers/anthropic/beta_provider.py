"""Beta Anthropic provider implementation."""

from anthropic import Anthropic, AsyncAnthropic

from .base_beta_provider import BaseAnthropicBetaProvider


class AnthropicBetaProvider(BaseAnthropicBetaProvider):
    """Provider using beta Anthropic API."""

    id = "anthropic-beta"
    default_scope = "anthropic-beta/"

    def __init__(
        self, *, api_key: str | None = None, base_url: str | None = None
    ) -> None:
        """Initialize the beta Anthropic client."""
        self.client = Anthropic(api_key=api_key, base_url=base_url)
        self.async_client = AsyncAnthropic(api_key=api_key, base_url=base_url)
