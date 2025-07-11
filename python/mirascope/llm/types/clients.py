from typing_extensions import TypeVar

from ..clients.base import BaseClient, BaseParams
from ..clients.register import REGISTERED_LLMS

ProviderMessageT = TypeVar("ProviderMessageT")
"""Type variable for an LLM that is usable by a specific LLM provider.

May often be the union of generic `llm.Message` and a provider-specific message representation."""

ParamsT = TypeVar("ParamsT", bound="BaseParams")
ClientT = TypeVar("ClientT", bound="BaseClient")
LLMT = TypeVar("LLMT", bound=REGISTERED_LLMS)
