"""Global test configuration for mirascope tests.

This module provides shared fixtures and configuration for all tests in the
mirascope test suite, including VCR configuration for HTTP recording/playback.
"""

import pytest
from typing_extensions import TypedDict


class VCRConfig(TypedDict):
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
    - 'body': Request body content
    - 'headers': Request headers
    """

    filter_headers: list[str]
    """Headers to filter out from recordings for security/privacy.
    
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


@pytest.fixture(scope="session")
def vcr_config() -> VCRConfig:
    """VCR configuration for all API tests.

    Uses session scope since VCR configuration is static and can be shared
    across all test modules in a session. This covers all major LLM providers:
    - OpenAI (authorization header)
    - Google/Gemini (x-goog-api-key header)
    - Anthropic (x-api-key, anthropic-organization-id headers)

    Returns:
        VCRConfig: Dictionary with VCR.py configuration settings
    """
    return {
        "record_mode": "once",
        "match_on": ["method", "uri", "body"],
        "filter_headers": [
            "authorization",  # OpenAI Bearer tokens
            "x-api-key",  # Anthropic API keys
            "x-goog-api-key",  # Google/Gemini API keys
            "anthropic-organization-id",  # Anthropic org identifiers
        ],
        "filter_post_data_parameters": [],
    }
