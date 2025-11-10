"""Utilities for managing cached LLM client singletons."""

from .anthropic import clear_cache as clear_anthropic_cache
from .azure_openai.completions import clear_cache as clear_azure_completions_cache
from .azure_openai.responses import clear_cache as clear_azure_responses_cache
from .google import clear_cache as clear_google_cache
from .openai import (
    clear_completions_cache as clear_openai_completions_cache,
    clear_responses_cache as clear_openai_responses_cache,
)

__all__ = ["clear_all_client_caches"]


def clear_all_client_caches() -> None:
    """Clear caches for all registered LLM client implementations."""

    clear_anthropic_cache()
    clear_azure_completions_cache()
    clear_azure_responses_cache()
    clear_google_cache()
    clear_openai_completions_cache()
    clear_openai_responses_cache()
