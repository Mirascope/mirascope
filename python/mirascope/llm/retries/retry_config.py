"""Configuration for retry behavior."""

from typing_extensions import TypedDict


class RetryConfig(TypedDict, total=False):
    """Configuration for retry behavior.

    This is an empty TypedDict for now, to be populated with retry configuration
    options as the retry logic is implemented.

    Future fields may include:
    - max_attempts: Maximum number of retry attempts
    - backoff: Backoff strategy configuration
    - retry_on: Tuple of exception types to retry on
    - fallback_models: List of fallback model IDs
    - retry_on_validation_error: Whether to retry on validation errors
    - validation_error_formatter: Function to format validation errors
    - max_validation_retries: Maximum validation retry attempts
    """
