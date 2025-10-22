"""Utilities for managing cached LLM client singletons."""

from .providers import PROVIDER_REGISTRY

__all__ = ["clear_all_client_caches"]


def clear_all_client_caches() -> None:
    """Clear caches for all registered LLM client implementations."""

    for clear_cache_fn in PROVIDER_REGISTRY.values():
        clear_cache_fn()
