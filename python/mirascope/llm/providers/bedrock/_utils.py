"""Shared Bedrock provider utilities."""

from __future__ import annotations


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
        return model_id.split("/", 1)[1]
    return model_id


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
