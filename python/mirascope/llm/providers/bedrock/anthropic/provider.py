"""Bedrock Anthropic provider implementation."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, ClassVar

import httpx
from anthropic import Anthropic, AnthropicBedrock, AsyncAnthropic, AsyncAnthropicBedrock

from ...anthropic import _utils as anthropic_utils
from ...anthropic.provider import BaseAnthropicProvider
from .. import _utils as bedrock_utils
from ..model_id import BedrockModelId

if TYPE_CHECKING:
    from ....formatting import Format, FormattableT, OutputParser
    from ....tools import AnyToolSchema, BaseToolkit


class BedrockAnthropicApiKeyClient(AnthropicBedrock):
    """AnthropicBedrock client that uses API key authentication instead of SigV4.

    This client overrides _prepare_request to inject a Bearer token for
    Bedrock's API key authentication, bypassing the default SigV4 signing.

    Note:
        The parent's _prepare_request only adds SigV4 authentication headers via
        get_auth_headers(). Since API key auth uses Bearer tokens instead, we
        intentionally skip the parent's implementation to avoid conflicting auth
        headers. This was verified against anthropic SDK v0.52.0+. SDK updates
        may require re-verification.
    """

    def __init__(
        self, api_key: str, aws_region: str, base_url: str | None = None
    ) -> None:
        self._bearer_token = api_key
        super().__init__(
            aws_region=aws_region,
            base_url=base_url,
        )

    def _prepare_request(self, request: httpx.Request) -> None:
        request.headers["Authorization"] = f"Bearer {self._bearer_token}"


class AsyncBedrockAnthropicApiKeyClient(AsyncAnthropicBedrock):
    """Async AnthropicBedrock client that uses API key authentication instead of SigV4.

    This client overrides _prepare_request to inject a Bearer token for
    Bedrock's API key authentication, bypassing the default SigV4 signing.

    Note:
        The parent's _prepare_request only adds SigV4 authentication headers via
        get_auth_headers(). Since API key auth uses Bearer tokens instead, we
        intentionally skip the parent's implementation to avoid conflicting auth
        headers. This was verified against anthropic SDK v0.52.0+. SDK updates
        may require re-verification.
    """

    def __init__(
        self, api_key: str, aws_region: str, base_url: str | None = None
    ) -> None:
        self._bearer_token = api_key
        super().__init__(
            aws_region=aws_region,
            base_url=base_url,
        )

    async def _prepare_request(self, request: httpx.Request) -> None:
        request.headers["Authorization"] = f"Bearer {self._bearer_token}"


class BedrockAnthropicProvider(
    BaseAnthropicProvider[
        AnthropicBedrock,
        AsyncAnthropicBedrock,
        Anthropic,
        AsyncAnthropic,
    ]
):
    """Provider for Anthropic models on Amazon Bedrock."""

    id: ClassVar[str] = "bedrock:anthropic"
    default_scope: ClassVar[str | list[str]] = bedrock_utils.default_anthropic_scopes()
    api_key_env_var: ClassVar[str] = "AWS_BEARER_TOKEN_BEDROCK"
    error_map = anthropic_utils.ANTHROPIC_ERROR_MAP

    def __init__(
        self,
        *,
        api_key: str | None = None,
        aws_region: str | None = None,
        aws_access_key: str | None = None,
        aws_secret_key: str | None = None,
        aws_session_token: str | None = None,
        aws_profile: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialize the Bedrock Anthropic provider.

        Args:
            api_key: Optional API key for authentication. If provided, this takes
                priority over AWS credentials. Falls back to AWS_BEARER_TOKEN_BEDROCK
                environment variable.
            aws_region: AWS region for Bedrock. Defaults to environment configuration.
            aws_access_key: AWS access key ID. Defaults to environment configuration.
            aws_secret_key: AWS secret access key. Defaults to environment configuration.
            aws_session_token: AWS session token for temporary credentials.
            aws_profile: AWS profile name for credentials. Defaults to environment.
            base_url: Custom base URL for Bedrock endpoint (e.g., for GovCloud).
        """
        resolved_api_key = api_key or os.environ.get(self.api_key_env_var)
        resolved_region = bedrock_utils.resolve_region(
            aws_region, aws_profile=aws_profile
        )

        if resolved_api_key:
            self.client = BedrockAnthropicApiKeyClient(
                api_key=resolved_api_key,
                aws_region=resolved_region,
                base_url=base_url,
            )
            self.async_client = AsyncBedrockAnthropicApiKeyClient(
                api_key=resolved_api_key,
                aws_region=resolved_region,
                base_url=base_url,
            )
        else:
            # SigV4 authentication via AnthropicBedrock client.
            # Requires boto3/botocore (anthropic[bedrock] extra or mirascope[bedrock]).
            # If missing, the SDK raises an error at request time.
            self.client = AnthropicBedrock(
                aws_region=aws_region,
                aws_access_key=aws_access_key,
                aws_secret_key=aws_secret_key,
                aws_session_token=aws_session_token,
                aws_profile=aws_profile,
                base_url=base_url,
            )
            self.async_client = AsyncAnthropicBedrock(
                aws_region=aws_region,
                aws_access_key=aws_access_key,
                aws_secret_key=aws_secret_key,
                aws_session_token=aws_session_token,
                aws_profile=aws_profile,
                base_url=base_url,
            )

    def get_error_status(self, e: Exception) -> int | None:
        """Extract HTTP status code from Anthropic exception."""
        return getattr(e, "status_code", None)

    def _model_name(self, model_id: str) -> str:
        return bedrock_utils.bedrock_model_name(model_id)

    def _error_provider_id(self) -> str:
        return "anthropic"

    def _should_use_beta(
        self,
        model_id: BedrockModelId,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None,
        toolkit: BaseToolkit[AnyToolSchema],
    ) -> bool:
        """Bedrock doesn't expose the beta API; always use the standard API."""
        return False


class BedrockAnthropicRoutedProvider(BedrockAnthropicProvider):
    """Bedrock Anthropic provider that reports provider_id as 'bedrock'."""

    id: ClassVar[str] = "bedrock"
