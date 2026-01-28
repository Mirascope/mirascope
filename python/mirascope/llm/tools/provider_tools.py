"""Base class for provider-native tools."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderTool:
    """Base class for tools executed natively by providers.

    Unlike regular tools which define functions that you execute locally,
    provider tools are capabilities built into the provider's API.
    The provider handles execution entirely server-side.

    Provider tools have no sync/async distinction since they are not
    executed by your code - they are configuration passed to the provider.
    """

    name: str
