"""Configuration for Mirascope end to end tests.

Includes setting up VCR for HTTP recording/playback.
"""

from __future__ import annotations

import hashlib
import inspect
import re
from collections.abc import Awaitable, Callable, Generator
from copy import deepcopy
from typing import ParamSpec, TypedDict, get_args
from typing_extensions import TypeIs

import httpx
import pytest
from anthropic.lib.bedrock import _auth as bedrock_auth
from anthropic.lib.bedrock._client import AnthropicBedrock, AsyncAnthropicBedrock
from vcr.cassette import Cassette as VCRCassette
from vcr.request import Request as VCRRequest
from vcr.stubs import httpx_stubs

from mirascope import llm
from mirascope.llm.clients import clear_all_client_caches

P = ParamSpec("P")

PROVIDER_MODEL_ID_PAIRS: list[tuple[llm.Provider, llm.ModelId]] = [
    ("anthropic", "claude-sonnet-4-0"),
    ("anthropic-bedrock", "us.anthropic.claude-haiku-4-5-20251001-v1:0"),
    ("azure-openai:completions", "gpt-4o-mini"),
    ("azure-openai:responses", "gpt-4o-mini"),
    ("google", "gemini-2.5-flash"),
    ("openai:completions", "gpt-4o"),
    ("openai:responses", "gpt-4o"),
]


FORMATTING_MODES: tuple[llm.FormattingMode | None] = get_args(llm.FormattingMode) + (
    None,
)

SENSITIVE_HEADERS = [
    # Common API authentication headers
    "api-key",
    "authorization",
    "x-api-key",
    "x-goog-api-key",
    "anthropic-organization-id",
    "cookie",
    # AWS SigV4 headers (Bedrock)
    "x-amz-date",
    "x-amz-security-token",
    "x-amz-content-sha256",
    "amz-sdk-invocation-id",
    "amz-sdk-request",
]


class VCRConfig(TypedDict, total=False):
    """Configuration for VCR.py HTTP recording and playback.

    VCR.py is used to record HTTP interactions during tests and replay them
    in subsequent test runs, making tests faster and more reliable.
    """

    record_mode: str
    """How VCR should handle recording. 'once' means record once then replay.

    Options:
    - 'once': Record interactions once, then always replay from cassette
    - 'new_episodes': Record new interactions, replay existing ones
    - 'all': Always record, overwriting existing cassettes
    - 'none': Never record, only replay (will fail if cassette missing)
    """

    match_on: list[str]
    """HTTP request attributes to match when finding recorded interactions.

    Common options:
    - 'method': HTTP method (GET, POST, etc.)
    - 'uri': Request URI/URL
    - 'body': Request body content (use 'raw_body' for exact binary matching)
    - 'headers': Request headers
    - 'scheme', 'host', 'port', 'path', 'query': URL components
    """

    filter_headers: list[str]
    """Headers to filter out from recordings for security/privacy.

    DEPRECATED: Use before_record_request instead for better control.
    These headers will be removed from both recorded cassettes and
    when matching requests during playback. Commonly used for:
    - Authentication tokens
    - API keys
    - Organization identifiers
    """

    filter_post_data_parameters: list[str]
    """POST data parameters to filter out from recordings.

    Similar to filter_headers but for form data and request body parameters.
    Useful for removing sensitive data from request bodies.
    """

    before_record_request: Callable[[VCRRequest], VCRRequest]
    """Callback to sanitize requests before saving to cassette.

    This function is called AFTER the real HTTP request is sent (with valid auth),
    but BEFORE it's written to the cassette file. Use this to sanitize sensitive
    headers without affecting the actual HTTP requests.
    """

    decode_compressed_response: bool
    """Whether to decode compressed responses.

    When False, VCR will preserve the exact bytes of compressed responses
    without decoding them. This is important for maintaining data integrity
    and avoiding issues with binary data or signatures.
    """


def sanitize_request(request: VCRRequest) -> VCRRequest:
    """Sanitize sensitive headers in VCR request before recording to cassette.

    This hook is called AFTER the real HTTP request is sent (with valid auth),
    but BEFORE it's written to the cassette file. We deep copy the request
    and replace sensitive headers with placeholders.

    Also normalizes Azure OpenAI URLs to use a dummy endpoint so that
    cassettes work in CI without real Azure credentials.

    Args:
        request: VCR request object to sanitize

    Returns:
        Sanitized copy of the request safe for cassette storage
    """
    request = deepcopy(request)

    if ".openai.azure.com" in request.uri:
        request.uri = re.sub(
            r"https://[^/]+\.openai\.azure\.com",
            "https://dummy.openai.azure.com",
            request.uri,
        )

    for header in SENSITIVE_HEADERS:
        header_lower = header.lower()
        for req_header in list(request.headers.keys()):
            if req_header.lower() == header_lower:
                if isinstance(request.headers[req_header], list):
                    request.headers[req_header] = ["<filtered>"]
                else:
                    request.headers[req_header] = "<filtered>"

    return request


@pytest.fixture(autouse=True)
def _clear_client_caches() -> None:
    """Ensure cached LLM client singletons do not bleed across e2e tests."""
    clear_all_client_caches()


@pytest.fixture(scope="session")
def vcr_config() -> VCRConfig:
    """VCR configuration for all API tests.

    Uses session scope since VCR configuration is static and can be shared
    across all test modules in a session. This covers all major LLM providers:
    - OpenAI (authorization header)
    - Google/Gemini (x-goog-api-key header)
    - Anthropic (x-api-key, anthropic-organization-id headers)
    - AWS Bedrock (AWS SigV4 headers: authorization, x-amz-*)

    Note:
        We use before_record_request hook for sanitizing sensitive headers.
        This ensures the real HTTP requests (with valid auth) are sent
        successfully, but sensitive headers are replaced with placeholders
        in the cassette files.

        We use 'raw_body' in match_on for exact binary matching and
        decode_compressed_response=False to preserve exact response bytes
        (important for AWS SigV4 signatures and binary data integrity).

    Returns:
        VCRConfig: Dictionary with VCR.py configuration settings
    """
    return {
        "record_mode": "once",
        "match_on": ["method", "uri", "body"],
        "filter_headers": [],  # Don't filter here; use before_record_request
        "filter_post_data_parameters": [],
        "before_record_request": sanitize_request,
        "decode_compressed_response": False,  # Preserve exact response bytes
    }


def _remove_auth_headers(headers: httpx.Headers) -> None:
    """Remove stale AWS authentication headers before re-signing.

    AWS SigV4 signatures include a timestamp (x-amz-date) and are computed
    based on the request at that specific moment. When we need to recompute
    the signature (after VCR consumes the body), we must remove the old
    auth headers to prevent conflicts with the new signature.

    Args:
        headers: The httpx.Headers object to modify in-place
    """
    for header_name in ["authorization", "x-amz-date"]:
        if header_name in headers:
            del headers[header_name]


def _compute_bedrock_signature(
    request: httpx.Request,
    bedrock_client: AnthropicBedrock | AsyncAnthropicBedrock,
) -> dict[str, str]:
    """Compute AWS SigV4 signature headers for Bedrock request.

    AWS Bedrock requires AWS SigV4 signatures that include a hash of the request
    body. The Anthropic Bedrock SDK injects these signatures directly into httpx
    requests (it doesn't use botocore internally), so we need to manually
    recompute signatures when VCR.py consumes the request body stream.

    Why this is necessary:
    1. Bedrock SDK signs the request with body hash
    2. VCR.py reads the body to match against cassettes
    3. Reading the body stream consumes it (becomes empty)
    4. Without re-signing, the empty body would be sent with the original
       signature, causing authentication failures

    Args:
        request: The httpx request that needs signing
        bedrock_client: The Bedrock client containing AWS credentials

    Returns:
        Dictionary of AWS SigV4 signature headers (authorization, x-amz-date, etc.)
    """
    body_bytes = request.read() or b""
    try:
        body_text = body_bytes.decode()
    except UnicodeDecodeError:
        body_text = ""

    payload_hash = hashlib.sha256(body_bytes).hexdigest()
    request.headers["x-amz-content-sha256"] = payload_hash

    headers_for_signing = httpx.Headers(request.headers)
    _remove_auth_headers(headers_for_signing)

    return bedrock_auth.get_auth_headers(
        method=request.method,
        url=str(request.url),
        headers=headers_for_signing,
        aws_access_key=bedrock_client.aws_access_key,
        aws_secret_key=bedrock_client.aws_secret_key,
        aws_session_token=bedrock_client.aws_session_token,
        region=bedrock_client.aws_region,
        profile=bedrock_client.aws_profile,
        data=body_text,
    )


@pytest.fixture(scope="session", autouse=True)
def _bedrock_resign_vcr_httpx() -> Generator[None, None, None]:
    """Re-sign Bedrock requests after VCR consumes the body.

    This fixture solves a fundamental incompatibility between VCR.py and AWS SigV4
    authentication used by Bedrock:

    The Problem:
    - AWS Bedrock SDK injects SigV4 signatures into httpx requests (no botocore)
    - VCR.py intercepts requests and reads the body to match against cassettes
    - HTTP request bodies are streams that can only be read once
    - After VCR reads the body, it becomes empty
    - Sending an empty body with the original signature causes auth failures

    The Solution:
    This fixture patches VCR.py's httpx integration to:
    1. Detect Bedrock requests (by checking for 'bedrock-runtime' in hostname)
    2. After VCR reads the body, restore it from the saved bytes
    3. Remove stale auth headers (authorization, x-amz-date)
    4. Recompute AWS SigV4 signatures with the restored body
    5. Send the request with fresh signatures

    Technical Details:
    - We attach a re-signing callback to request.extensions during _prepare_request
    - VCR's _sync_vcr_send/_async_vcr_send are patched to invoke this callback
    - The callback recomputes signatures using the Anthropic SDK's bedrock_auth module
    - This ensures VCR recording/playback works while maintaining valid AWS auth
    """
    original_prepare_sync = AnthropicBedrock._prepare_request
    original_prepare_async = AsyncAnthropicBedrock._prepare_request

    def _attach_resigner_sync(self: AnthropicBedrock, request: httpx.Request) -> None:
        original_prepare_sync(self, request)

        def _resign_sync() -> None:
            signed_headers = _compute_bedrock_signature(request, self)
            request.headers.update(signed_headers)

        request.extensions["mirascope_bedrock_resign"] = _resign_sync

    async def _attach_resigner_async(
        self: AsyncAnthropicBedrock, request: httpx.Request
    ) -> None:
        await original_prepare_async(self, request)

        async def _resign_async() -> None:
            signed_headers = _compute_bedrock_signature(request, self)
            request.headers.update(signed_headers)

        request.extensions["mirascope_bedrock_resign_async"] = _resign_async

    AnthropicBedrock._prepare_request = _attach_resigner_sync
    AsyncAnthropicBedrock._prepare_request = _attach_resigner_async

    original_shared_send = httpx_stubs._shared_vcr_send
    original_sync_send = httpx_stubs._sync_vcr_send
    original_async_send = httpx_stubs._async_vcr_send

    def _is_bedrock_request(request: httpx.Request | None) -> TypeIs[httpx.Request]:
        """Check if the request is targeting AWS Bedrock API.

        We identify Bedrock requests by checking for 'bedrock-runtime' in the
        hostname (e.g., bedrock-runtime.us-west-2.amazonaws.com). This allows
        us to selectively apply the re-signing logic only to Bedrock requests,
        avoiding unnecessary overhead for other providers.

        Args:
            request: The httpx request to check (can be None)

        Returns:
            True if this is a Bedrock API request, False otherwise
        """
        if request is None:
            return False
        url = getattr(request, "url", None)
        host = getattr(url, "host", "") if url is not None else ""
        return bool(host and "bedrock-runtime" in host)

    def _reset_request_body(request: httpx.Request, body_bytes: bytes) -> None:
        """Reset request body stream and content-length header.

        HTTP request bodies are streams that can only be read once. After reading
        (e.g., by VCR.py or during signature computation), we must restore the
        stream with the saved bytes so it can be read again or sent over the network.

        Args:
            request: The httpx request to modify
            body_bytes: The saved body content to restore
        """
        request.stream = httpx.ByteStream(body_bytes)
        request._content = body_bytes
        request.headers["content-length"] = str(len(body_bytes))

    def _handle_bedrock_resign_sync(real_request: httpx.Request) -> None:
        """Re-sign Bedrock request with fresh AWS SigV4 signature (synchronous).

        This is called after VCR has consumed the request body stream. We:
        1. Save the body bytes (reading consumes the stream)
        2. Restore the body stream for signature computation
        3. Remove old auth headers
        4. Compute new signature (this reads the body again)
        5. Restore the body stream again for the actual HTTP send

        Args:
            real_request: The httpx request to re-sign
        """
        body_bytes = real_request.read() or b""
        _reset_request_body(real_request, body_bytes)

        resign_sync = real_request.extensions.get("mirascope_bedrock_resign")
        if inspect.isfunction(resign_sync):
            _remove_auth_headers(real_request.headers)
            resign_sync()
            _reset_request_body(real_request, body_bytes)

    async def _handle_bedrock_resign_async(real_request: httpx.Request) -> None:
        """Re-sign Bedrock request with fresh AWS SigV4 signature (asynchronous).

        Same as _handle_bedrock_resign_sync but handles async resign callbacks.
        Falls back to sync callback if async callback is not available.

        Args:
            real_request: The httpx request to re-sign
        """
        body_bytes = real_request.read() or b""
        _reset_request_body(real_request, body_bytes)

        resign_async = real_request.extensions.get("mirascope_bedrock_resign_async")
        resign_sync = real_request.extensions.get("mirascope_bedrock_resign")

        if inspect.iscoroutinefunction(resign_async):
            _remove_auth_headers(real_request.headers)
            await resign_async()
            _reset_request_body(real_request, body_bytes)
        elif inspect.isfunction(resign_sync):
            _remove_auth_headers(real_request.headers)
            resign_sync()
            _reset_request_body(real_request, body_bytes)

    def _patched_sync_send(
        cassette: VCRCassette,
        real_send: Callable[..., httpx.Response],
        client: httpx.Client,
        request: httpx.Request,
        **kwargs: object,
    ) -> httpx.Response:
        args = (client, request)
        vcr_request, response = original_shared_send(
            cassette, real_send, *args, **kwargs
        )
        real_request: httpx.Request | None = request

        if response is not None:
            client.cookies.extract_cookies(response)
            return response

        if _is_bedrock_request(real_request):
            _handle_bedrock_resign_sync(real_request)

        real_response = real_send(*args, **kwargs)
        httpx_stubs._run_async_function(
            httpx_stubs._record_responses,
            cassette,
            vcr_request,
            real_response,
            aread=False,
        )
        return real_response

    async def _patched_async_send(
        cassette: VCRCassette,
        real_send: Callable[..., Awaitable[httpx.Response]],
        client: httpx.AsyncClient,
        request: httpx.Request,
        **kwargs: object,
    ) -> httpx.Response:
        # VCR expects args tuple, so reconstruct it for original_shared_send
        args = (client, request)
        vcr_request, response = original_shared_send(
            cassette, real_send, *args, **kwargs
        )
        real_request: httpx.Request | None = request

        if response is not None:
            client.cookies.extract_cookies(response)
            return response

        if _is_bedrock_request(real_request):
            await _handle_bedrock_resign_async(real_request)

        real_response = await real_send(*args, **kwargs)
        await httpx_stubs._record_responses(
            cassette, vcr_request, real_response, aread=True
        )
        return real_response

    httpx_stubs._sync_vcr_send = _patched_sync_send
    httpx_stubs._async_vcr_send = _patched_async_send
    try:
        yield
    finally:
        httpx_stubs._sync_vcr_send = original_sync_send
        httpx_stubs._async_vcr_send = original_async_send
        httpx_stubs._shared_vcr_send = original_shared_send
        AnthropicBedrock._prepare_request = original_prepare_sync
        AsyncAnthropicBedrock._prepare_request = original_prepare_async


class ProviderRequest(pytest.FixtureRequest):
    """Request for the `provider` fixture parameter."""

    param: llm.Provider


@pytest.fixture
def provider(request: ProviderRequest) -> llm.Provider:
    """Get provider from test parameters."""
    return request.param


class ModelIdRequest(pytest.FixtureRequest):
    """Request for the `model_id` fixture parameter."""

    param: llm.ModelId


@pytest.fixture
def model_id(request: ModelIdRequest) -> llm.ModelId:
    """Get model_id from test parameters."""
    return request.param


class FormattingModeRequest(pytest.FixtureRequest):
    """Request for the `formatting_mode` fixture parameter.

    If `formatting_mode` is `None`, then accessing param will raise `AttributeError`.
    """

    param: llm.FormattingMode


@pytest.fixture
def formatting_mode(
    request: FormattingModeRequest,
) -> llm.FormattingMode | None:
    """Get formatting_mode from test parameters."""
    if hasattr(request, "param"):
        return request.param
    else:
        return None


# Symbols to automatically import from mirascope.llm so that snapshots are valid
# python. (Ruff --fix will clean out unused symbols)
SNAPSHOT_IMPORT_SYMBOLS = [
    "AssistantMessage",
    "Audio",
    "Base64ImageSource",
    "Base64AudioSource",
    "FinishReason",
    "Format",
    "Image",
    "SystemMessage",
    "Text",
    "TextChunk",
    "TextEndChunk",
    "TextStartChunk",
    "Thought",
    "ToolCall",
    "ToolCallChunk",
    "ToolCallEndChunk",
    "ToolCallStartChunk",
    "ToolOutput",
    "URLImageSource",
    "UserMessage",
]
