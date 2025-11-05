"""Anthropic Bedrock client implementation."""

import os
from contextvars import ContextVar
from functools import lru_cache
from typing import Literal

from anthropic.lib.bedrock._client import AnthropicBedrock, AsyncAnthropicBedrock

from .base_client import BaseAnthropicClient

ANTHROPIC_BEDROCK_CLIENT_CONTEXT: ContextVar["AnthropicBedrockClient | None"] = (
    ContextVar("ANTHROPIC_BEDROCK_CLIENT_CONTEXT", default=None)
)


@lru_cache(maxsize=256)
def _anthropic_bedrock_singleton(
    base_url: str | None,
    aws_region: str | None,
    aws_access_key: str | None,
    aws_secret_key: str | None,
    aws_session_token: str | None,
    aws_profile: str | None,
) -> "AnthropicBedrockClient":  # pragma: no cover
    """Return a cached AnthropicBedrockClient instance for the given parameters."""
    # TODO: Add test coverage for AnthropicBedrockClient in separate test branch
    return AnthropicBedrockClient(
        base_url=base_url,
        aws_region=aws_region,
        aws_access_key=aws_access_key,
        aws_secret_key=aws_secret_key,
        aws_session_token=aws_session_token,
        aws_profile=aws_profile,
    )


def client(
    *,
    base_url: str | None = None,
    aws_region: str | None = None,
    aws_access_key: str | None = None,
    aws_secret_key: str | None = None,
    aws_session_token: str | None = None,
    aws_profile: str | None = None,
) -> "AnthropicBedrockClient":
    """Return an `AnthropicBedrockClient`.

    Args:
        base_url: Override the default Bedrock endpoint URL.
            Useful for Gov/isolated regions or custom proxies.
        aws_region: AWS region. If None, uses AWS_REGION env var or default region.
        aws_access_key: AWS access key. If None, uses AWS_ACCESS_KEY_ID env var.
        aws_secret_key: AWS secret key. If None, uses AWS_SECRET_ACCESS_KEY env var.
        aws_session_token: AWS session token. If None, uses AWS_SESSION_TOKEN env var.
        aws_profile: AWS profile name. If None, uses AWS_PROFILE env var.

    Returns:
        An `AnthropicBedrockClient` instance.

    Examples:
        # Use environment variables
        client = client()

        # Use explicit credentials
        client = client(
            aws_region="us-west-2",
            aws_access_key="your-access-key",
            aws_secret_key="your-secret-key"
        )

        # Use AWS profile
        client = client(aws_profile="production")

        # Use custom endpoint (Gov Cloud, isolated regions, etc.)
        client = client(
            aws_region="us-gov-west-1",
            base_url="https://bedrock-runtime.us-gov-west-1.amazonaws.com"
        )
    """
    # TODO: Add test coverage for client() function in separate test branch
    aws_region = aws_region or os.getenv("AWS_REGION")  # pragma: no cover
    aws_access_key = aws_access_key or os.getenv(
        "AWS_ACCESS_KEY_ID"
    )  # pragma: no cover
    aws_secret_key = aws_secret_key or os.getenv(
        "AWS_SECRET_ACCESS_KEY"
    )  # pragma: no cover
    aws_session_token = aws_session_token or os.getenv(
        "AWS_SESSION_TOKEN"
    )  # pragma: no cover
    aws_profile = aws_profile or os.getenv("AWS_PROFILE")  # pragma: no cover

    return _anthropic_bedrock_singleton(  # pragma: no cover
        base_url,
        aws_region,
        aws_access_key,
        aws_secret_key,
        aws_session_token,
        aws_profile,
    )


def clear_cache() -> None:  # pragma: no cover
    """Clear the client singleton cache.

    This is useful for testing or when you need to force recreation
    of clients with updated configuration.
    """
    # TODO: Add test coverage for clear_cache() in separate test branch
    _anthropic_bedrock_singleton.cache_clear()


def get_client() -> "AnthropicBedrockClient":  # pragma: no cover
    """Retrieve the current Anthropic Bedrock client from context, or a global default.

    Returns:
        The current Anthropic Bedrock client from context if available, otherwise
        a global default client based on environment variables.
    """
    # TODO: Add test coverage for get_client() in separate test branch
    ctx_client = ANTHROPIC_BEDROCK_CLIENT_CONTEXT.get()
    return ctx_client or client()


class AnthropicBedrockClient(
    BaseAnthropicClient[
        AnthropicBedrock, AsyncAnthropicBedrock, "AnthropicBedrockClient"
    ]
):
    """Anthropic Bedrock client that inherits from BaseAnthropicClient.

    Only overrides initialization to use Bedrock-specific SDK classes and
    provider naming to return 'anthropic-bedrock'.
    """

    @property
    def _context_var(
        self,
    ) -> ContextVar["AnthropicBedrockClient | None"]:  # pragma: no cover
        # TODO: Add test coverage for _context_var property in separate test branch
        return ANTHROPIC_BEDROCK_CLIENT_CONTEXT

    def __init__(  # pragma: no cover
        self,
        *,
        base_url: str | None = None,
        aws_region: str | None = None,
        aws_access_key: str | None = None,
        aws_secret_key: str | None = None,
        aws_session_token: str | None = None,
        aws_profile: str | None = None,
    ) -> None:
        """Initialize the Anthropic Bedrock client.

        Args:
            base_url: Override the default Bedrock endpoint URL.
                Useful for Gov/isolated regions or custom proxies.
            aws_region: AWS region for Bedrock.
            aws_access_key: AWS access key for authentication.
            aws_secret_key: AWS secret key for authentication.
            aws_session_token: AWS session token for temporary credentials.
            aws_profile: AWS profile name for credential lookup.
        """
        # TODO: Add test coverage for __init__ in separate test branch
        self.client = AnthropicBedrock(
            base_url=base_url,
            aws_region=aws_region,
            aws_access_key=aws_access_key,
            aws_secret_key=aws_secret_key,
            aws_session_token=aws_session_token,
            aws_profile=aws_profile,
        )
        self.async_client = AsyncAnthropicBedrock(
            base_url=base_url,
            aws_region=aws_region,
            aws_access_key=aws_access_key,
            aws_secret_key=aws_secret_key,
            aws_session_token=aws_session_token,
            aws_profile=aws_profile,
        )

    @property
    def provider(self) -> Literal["anthropic-bedrock"]:  # pragma: no cover
        """Return the provider name for Anthropic Bedrock."""
        # TODO: Add test coverage for provider property in separate test branch
        return "anthropic-bedrock"
