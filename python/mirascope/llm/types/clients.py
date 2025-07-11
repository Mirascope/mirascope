from typing_extensions import TypeVar

from ..clients.base import BaseClient, BaseParams
from ..clients.register import REGISTERED_LLMS

ProviderMessageT = TypeVar("ProviderMessageT")
"""Type variable for an LLM that is usable by a specific LLM provider.

May often be the union of generic `llm.Message` and a provider-specific message representation."""

ParamsT = TypeVar("ParamsT", bound="BaseParams")
"""Type variable for LLM parameters. May be provider specific."""

ClientT = TypeVar("ClientT", bound="BaseClient")
"""Type variable for an LLM client."""

LLMT = TypeVar("LLMT", bound=REGISTERED_LLMS)
"""Type variable for a registered LLM model. Will be a string of form provider:model_name."""
