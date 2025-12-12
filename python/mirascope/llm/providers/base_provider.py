"""Base Provider class and context management for runtime provider overrides."""

from __future__ import annotations

from contextvars import ContextVar, Token
from types import TracebackType
from typing import TYPE_CHECKING, Any, Generic
from typing_extensions import TypeVar

if TYPE_CHECKING:
    from ..clients import BaseClient, ModelId

from .provider_id import ProviderId

# Type alias for provider scope (e.g., "anthropic/", "openai/")
ProviderScope = str

ClientT = TypeVar("ClientT", bound="BaseClient[str, Any]")

# Stack of provider overrides, each entry is (provider_instance, scope)
# We use Any for the provider type to allow any Provider[ClientT] subclass
PROVIDER_CONTEXT: ContextVar[list[tuple[Any, ProviderScope]] | None] = ContextVar(
    "PROVIDER_CONTEXT", default=None
)


def provider_for_model(model_id: ModelId) -> Provider[Any] | None:
    """Get the provider for a model from context, if any override matches.

    Checks the stack from most recent to least recent (last-wins semantics).
    Returns the Provider instance if a matching scope is found, None otherwise.

    Args:
        model_id: The full model ID (e.g., "anthropic/claude-4-5-sonnet")

    Returns:
        The Provider instance if a context override matches, None otherwise.
    """
    stack = PROVIDER_CONTEXT.get()
    if stack is None:
        return None

    for provider, scope in reversed(stack):
        if model_id.startswith(scope):
            return provider

    return None


class Provider(Generic[ClientT]):
    """A provider wraps a client and acts as a context manager to override provider routing.

    Providers enable routing model calls through different implementations at runtime.
    For example, you can route Anthropic models through the Together API by using a
    custom provider instance in a context manager.

    Example:
        ```python
        from mirascope import llm

        # Create a custom provider instance with specific API key
        custom_anthropic = llm.providers.AnthropicProvider(api_key="team-key")

        # Use it in a context to override the default provider
        with custom_anthropic:
            model = llm.use_model("anthropic/claude-4-5-sonnet")
            response = model.call(messages=[...])  # Uses the custom API key
        ```
    """

    provider_id: ProviderId
    """The provider identifier (e.g., "anthropic", "openai")."""

    default_scope: ProviderScope
    """The default scope this provider handles (e.g., "anthropic/", "openai/")."""

    def __init__(
        self,
        client: ClientT,
    ) -> None:
        """Initialize a Provider with a wrapped client.

        Args:
            client: The client instance to wrap.
        """
        self._client = client
        self._token_stack: list[Token[list[tuple[Any, ProviderScope]] | None]] = []

    @property
    def client(self) -> ClientT:
        """Get the wrapped client instance."""
        return self._client

    def __enter__(self) -> Provider[ClientT]:
        """Enter context manager - add this provider to the override stack."""
        current_stack = PROVIDER_CONTEXT.get()
        new_stack = (current_stack or []) + [(self, self.default_scope)]
        token = PROVIDER_CONTEXT.set(new_stack)
        self._token_stack.append(token)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit context manager - restore previous stack."""
        if self._token_stack:
            token = self._token_stack.pop()
            PROVIDER_CONTEXT.reset(token)
