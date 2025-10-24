"""Anthropic Vertex AI client implementation."""

import os
from contextvars import ContextVar
from functools import lru_cache
from typing import Literal

from anthropic import NOT_GIVEN
from anthropic.lib.vertex._client import AnthropicVertex, AsyncAnthropicVertex

from ..anthropic import BaseAnthropicClient

ANTHROPIC_VERTEX_CLIENT_CONTEXT: ContextVar["AnthropicVertexClient | None"] = (
    ContextVar("ANTHROPIC_VERTEX_CLIENT_CONTEXT", default=None)
)


@lru_cache(maxsize=256)
def _anthropic_vertex_singleton(
    project_id: str | None,
    region: str | None,
) -> "AnthropicVertexClient":
    """Return a cached AnthropicVertexClient instance for the given parameters."""
    return AnthropicVertexClient(
        project_id=project_id,
        region=region,
    )


def client(
    *,
    project_id: str | None = None,
    region: str | None = None,
) -> "AnthropicVertexClient":
    """Return an `AnthropicVertexClient`.

    Args:
        project_id: GCP project ID. If None, uses GOOGLE_CLOUD_PROJECT, GCLOUD_PROJECT,
            CLOUD_ML_PROJECT_ID, or GCP_PROJECT_ID env vars (in that order).
        region: GCP region. If None, uses CLOUD_ML_REGION, GOOGLE_CLOUD_REGION, or
            GOOGLE_CLOUD_LOCATION env vars (in that order).

    Returns:
        An `AnthropicVertexClient` instance.

    Examples:
        # Use environment variables
        client = client()

        # Use explicit parameters
        client = client(
            project_id="my-gcp-project",
            region="us-central1"
        )
    """
    project_id = (
        project_id
        or os.getenv("GOOGLE_CLOUD_PROJECT")
        or os.getenv("GCLOUD_PROJECT")
        or os.getenv("CLOUD_ML_PROJECT_ID")
        or os.getenv("GCP_PROJECT_ID")
    )
    region = (
        region
        or os.getenv("CLOUD_ML_REGION")
        or os.getenv("GOOGLE_CLOUD_REGION")
        or os.getenv("GOOGLE_CLOUD_LOCATION")
    )

    return _anthropic_vertex_singleton(
        project_id,
        region,
    )


def clear_cache() -> None:
    """Clear the client singleton cache and reset context.

    This is useful for testing or when you need to force recreation
    of clients with updated configuration.
    """
    _anthropic_vertex_singleton.cache_clear()
    ANTHROPIC_VERTEX_CLIENT_CONTEXT.set(None)


def get_client() -> "AnthropicVertexClient":
    """Retrieve the current Anthropic Vertex client from context, or a global default.

    Returns:
        The current Anthropic Vertex client from context if available, otherwise
        a global default client based on environment variables.
    """
    ctx_client = ANTHROPIC_VERTEX_CLIENT_CONTEXT.get()
    return ctx_client or client()


class AnthropicVertexClient(
    BaseAnthropicClient[AnthropicVertex, AsyncAnthropicVertex, "AnthropicVertexClient"]
):
    """Anthropic Vertex AI client that inherits from BaseAnthropicClient.

    Only overrides initialization to use Vertex-specific SDK classes and
    provider naming to return 'anthropic-vertex'.
    """

    @property
    def _context_var(self) -> ContextVar["AnthropicVertexClient | None"]:
        return ANTHROPIC_VERTEX_CLIENT_CONTEXT

    def __init__(
        self,
        *,
        project_id: str | None = None,
        region: str | None = None,
    ) -> None:
        """Initialize the Anthropic Vertex AI client.

        Args:
            project_id: GCP project ID.
            region: GCP region for Vertex AI.
        """
        self.client = AnthropicVertex(
            project_id=project_id or NOT_GIVEN,
            region=region or NOT_GIVEN,
        )
        self.async_client = AsyncAnthropicVertex(
            project_id=project_id or NOT_GIVEN,
            region=region or NOT_GIVEN,
        )

    @property
    def provider(self) -> Literal["anthropic-vertex"]:
        """Return the provider name for Anthropic Vertex AI."""
        return "anthropic-vertex"
