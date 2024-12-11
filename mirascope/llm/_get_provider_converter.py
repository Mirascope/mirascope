from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mirascope.llm._base_provider_converter import BaseProviderConverter


def _get_provider_converter(provider: str) -> type[BaseProviderConverter] | None:
    provider_converter: type[BaseProviderConverter] | None = None
    if provider == "openai":
        from mirascope.llm.providers.openai import OpenAIProviderConverter

        provider_converter = OpenAIProviderConverter
    return provider_converter
