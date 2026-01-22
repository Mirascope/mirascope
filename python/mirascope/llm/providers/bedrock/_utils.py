"""Shared Bedrock provider utilities."""

from __future__ import annotations

import os
from typing import Protocol, cast

DEFAULT_REGION = "us-east-1"


class _BotocoreSession(Protocol):
    def get_config_variable(
        self, logical_name: str, methods: object | None = None
    ) -> str | None: ...


def bedrock_model_name(model_id: str) -> str:
    """Extract the Bedrock model name from the model ID.

    Args:
        model_id: Full model ID (e.g. "bedrock/anthropic.claude-3-5-sonnet-20241022-v1:0"
            or "bedrock/us.anthropic.claude-3-5-sonnet-20241022-v1:0")

    Returns:
        Provider-specific model ID (e.g. "anthropic.claude-3-5-sonnet-20241022-v1:0"
            or "us.anthropic.claude-3-5-sonnet-20241022-v1:0")
    """
    if model_id.startswith("bedrock/"):
        return model_id.removeprefix("bedrock/")
    return model_id


def resolve_region(aws_region: str | None, *, aws_profile: str | None = None) -> str:
    """Resolve AWS region for Bedrock providers.

    Resolution order:
    1) Explicit aws_region argument
    2) AWS_REGION or AWS_DEFAULT_REGION environment variables
    3) AWS profile configuration (if provided and available)
    4) Fallback to us-east-1
    """
    if aws_region:
        return aws_region

    env_region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    if env_region:
        return env_region

    if aws_profile:
        try:
            from botocore.session import Session as BotocoreSession
        except ImportError:
            # botocore not installed; fall back to default region.
            # Note: If botocore IS installed but the profile doesn't exist,
            # we intentionally let the error propagate to inform the user.
            return DEFAULT_REGION

        session = cast(_BotocoreSession, BotocoreSession(profile=aws_profile))
        config_region = session.get_config_variable("region")
        if isinstance(config_region, str) and config_region:
            return config_region

    return DEFAULT_REGION


def default_anthropic_scopes() -> list[str]:
    """Return default Anthropic model ID prefixes for Bedrock routing.

    Returns:
        Sorted list of prefixes that identify Anthropic models on Bedrock,
        including base model IDs and cross-region inference profile prefixes.

    Note:
        ARN routing is handled separately by ``_is_anthropic_arn()`` in
        ``provider.py`` to avoid matching non-Anthropic ARNs via prefix matching.
    """
    scopes: set[str] = set()
    scopes.add("bedrock/anthropic.")
    for region_prefix in ("us.", "eu.", "apac.", "global."):
        scopes.add(f"bedrock/{region_prefix}anthropic.")
    return sorted(scopes)
