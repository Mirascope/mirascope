"""Bedrock OpenAI-compatible provider implementation."""

from __future__ import annotations

import os
from collections.abc import Generator
from typing import ClassVar, Protocol, cast

import httpx
from openai import AsyncOpenAI, OpenAI

from ...openai._utils.errors import OPENAI_ERROR_MAP
from ...openai.completions.base_provider import BaseOpenAICompletionsProvider
from .. import _utils as bedrock_utils


class _FrozenCredentials(Protocol):
    access_key: str
    secret_key: str
    token: str | None


class _BotocoreCredentials(Protocol):
    def get_frozen_credentials(self) -> _FrozenCredentials: ...


class _BotocoreSession(Protocol):
    def get_credentials(self) -> _BotocoreCredentials | None: ...


def _build_bedrock_openai_base_url(region: str) -> str:
    return f"https://bedrock-runtime.{region}.amazonaws.com/openai/v1"


class BedrockSigV4Auth(httpx.Auth):
    """Custom httpx Auth class for AWS SigV4 authentication.

    This class signs each outgoing request with AWS Signature Version 4,
    which is required for Bedrock's OpenAI-compatible endpoints when not
    using an API key.
    """

    requires_request_body = True

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        region: str,
        session_token: str | None = None,
    ) -> None:
        self._access_key = access_key
        self._secret_key = secret_key
        self._region = region
        self._session_token = session_token

    _HEADERS_TO_EXCLUDE = frozenset(
        {
            "authorization",
            "connection",
            "accept-encoding",
            "user-agent",
            "x-stainless-arch",
            "x-stainless-async",
            "x-stainless-lang",
            "x-stainless-os",
            "x-stainless-package-version",
            "x-stainless-read-timeout",
            "x-stainless-retry-count",
            "x-stainless-runtime",
            "x-stainless-runtime-version",
        }
    )

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        """Sign the request with AWS SigV4 and yield it."""
        from botocore.auth import SigV4Auth
        from botocore.awsrequest import AWSRequest
        from botocore.credentials import Credentials

        credentials = Credentials(
            self._access_key, self._secret_key, self._session_token
        )

        body_content = request.content.decode("utf-8") if request.content else None

        headers_for_signing = {
            key: value
            for key, value in request.headers.items()
            if key.lower() not in self._HEADERS_TO_EXCLUDE and value
        }

        aws_request = AWSRequest(
            method=request.method,
            url=str(request.url),
            data=body_content,
            headers=headers_for_signing,
        )

        class _SigV4Auth(Protocol):
            def add_auth(self, request: AWSRequest) -> None: ...

        auth = cast(_SigV4Auth, SigV4Auth(credentials, "bedrock", self._region))
        auth.add_auth(aws_request)

        if "authorization" in request.headers:
            del request.headers["authorization"]

        signed_headers = dict(aws_request.headers)
        for header_name, header_value in signed_headers.items():
            request.headers[header_name] = header_value

        yield request


def _resolve_aws_credentials(
    session: _BotocoreSession | None,
    aws_access_key_id: str | None,
    aws_secret_access_key: str | None,
    aws_session_token: str | None,
) -> tuple[str, str, str | None]:
    """Resolve AWS credentials from explicit args or botocore session.

    Raises:
        ValueError: If credentials cannot be resolved.
    """
    resolved_access_key: str | None = aws_access_key_id
    resolved_secret_key: str | None = aws_secret_access_key
    resolved_session_token: str | None = aws_session_token

    if not resolved_access_key or not resolved_secret_key:
        credentials = session.get_credentials() if session else None
        if credentials is not None:
            frozen = credentials.get_frozen_credentials()
            resolved_access_key = frozen.access_key
            resolved_secret_key = frozen.secret_key
            resolved_session_token = frozen.token

    if not resolved_access_key or not resolved_secret_key:
        raise ValueError(
            "Bedrock OpenAI-compatible API requires either an API key "
            "or AWS credentials. Set the AWS_ACCESS_KEY_ID and "
            "AWS_SECRET_ACCESS_KEY environment variables, configure a "
            "shared credentials/profile, or pass aws_access_key_id and "
            "aws_secret_access_key parameters."
        )

    return resolved_access_key, resolved_secret_key, resolved_session_token


def _create_sigv4_clients(
    base_url: str,
    access_key: str,
    secret_key: str,
    region: str,
    session_token: str | None,
) -> tuple[OpenAI, AsyncOpenAI]:
    """Create OpenAI clients with SigV4 authentication."""
    sigv4_auth = BedrockSigV4Auth(
        access_key=access_key,
        secret_key=secret_key,
        region=region,
        session_token=session_token,
    )

    sync_http_client = httpx.Client(auth=sigv4_auth)
    async_http_client = httpx.AsyncClient(auth=sigv4_auth)

    client = OpenAI(
        api_key="bedrock-sigv4",
        base_url=base_url,
        http_client=sync_http_client,
    )
    async_client = AsyncOpenAI(
        api_key="bedrock-sigv4",
        base_url=base_url,
        http_client=async_http_client,
    )

    return client, async_client


class BedrockOpenAIProvider(BaseOpenAICompletionsProvider):
    """Provider for Amazon Bedrock's OpenAI-compatible API.

    This provider uses the OpenAI SDK to communicate with Bedrock's OpenAI-compatible
    endpoints. It supports two authentication methods:

    1. API Key (Official): Use a Bedrock-issued API key via the api_key parameter
       or AWS_BEARER_TOKEN_BEDROCK environment variable.
    2. AWS SigV4 (Unofficial): Use IAM credentials for request signing. This is
       widely adopted but not officially documented for the OpenAI SDK.

    Note:
        OpenAI-compatible endpoints are only available for a subset of Bedrock models
        and regions. Check the AWS documentation for supported models and regions.
    """

    id: ClassVar[str] = "bedrock:openai"
    default_scope: ClassVar[str | list[str]] = "bedrock/openai."
    api_key_env_var: ClassVar[str] = "AWS_BEARER_TOKEN_BEDROCK"
    api_key_required: ClassVar[bool] = False
    provider_name: ClassVar[str | None] = "Amazon Bedrock (OpenAI-compatible)"
    error_map = OPENAI_ERROR_MAP

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        aws_region: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        aws_session_token: str | None = None,
        aws_profile: str | None = None,
    ) -> None:
        """Initialize the Bedrock OpenAI-compatible provider.

        Args:
            api_key: Optional API key for authentication. If provided, this takes
                priority over AWS credentials.
            base_url: Optional base URL override. If not provided, the URL will be
                constructed from the AWS region.
            aws_region: AWS region for the Bedrock endpoint. Defaults to the
                AWS_REGION or AWS_DEFAULT_REGION environment variable.
            aws_access_key_id: AWS access key ID. Defaults to the
                AWS_ACCESS_KEY_ID environment variable.
            aws_secret_access_key: AWS secret access key. Defaults to the
                AWS_SECRET_ACCESS_KEY environment variable.
            aws_session_token: AWS session token for temporary credentials.
                Defaults to the AWS_SESSION_TOKEN environment variable.
            aws_profile: AWS profile name for credentials. Defaults to environment.

        Raises:
            ValueError: If neither API key nor AWS credentials are available.
        """
        resolved_api_key = api_key or os.environ.get(self.api_key_env_var)
        resolved_region = bedrock_utils.resolve_region(
            aws_region, aws_profile=aws_profile
        )
        session: _BotocoreSession | None = None
        if not resolved_api_key:
            from botocore.session import Session as BotocoreSession

            session = cast(
                _BotocoreSession,
                BotocoreSession(profile=aws_profile)
                if aws_profile
                else BotocoreSession(),
            )

        resolved_base_url = base_url or _build_bedrock_openai_base_url(resolved_region)

        if resolved_api_key:
            self.client = OpenAI(
                api_key=resolved_api_key,
                base_url=resolved_base_url,
            )
            self.async_client = AsyncOpenAI(
                api_key=resolved_api_key,
                base_url=resolved_base_url,
            )
        else:
            access_key, secret_key, session_token = _resolve_aws_credentials(
                session,
                aws_access_key_id,
                aws_secret_access_key,
                aws_session_token,
            )
            self.client, self.async_client = _create_sigv4_clients(
                resolved_base_url,
                access_key,
                secret_key,
                resolved_region,
                session_token,
            )

    def get_error_status(self, e: Exception) -> int | None:
        """Extract HTTP status code from OpenAI exception."""
        return getattr(e, "status_code", None)

    def _model_name(self, model_id: str) -> str:
        if model_id.startswith("bedrock/"):
            model_name = model_id.split("/", 1)[1]
        else:  # pragma: no cover
            model_name = model_id

        return model_name


class BedrockOpenAIRoutedProvider(BedrockOpenAIProvider):
    """Bedrock OpenAI-compatible provider that reports provider_id as "bedrock"."""

    id: ClassVar[str] = "bedrock"
