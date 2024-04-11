"""Configuration for the Mirascope chroma module tests."""
import pytest

from mirascope.chroma.types import ChromaSettings
from mirascope.chroma.vectorstores import ChromaVectorStore


@pytest.fixture
def fixture_persistent_client() -> ChromaVectorStore:
    """Fixture for a persistent ChromaVectorStore."""

    class VectorStore(ChromaVectorStore):
        index_name = "test"
        client_settings = ChromaSettings(mode="persistent")

    return VectorStore()


@pytest.fixture
def fixture_http_client() -> ChromaVectorStore:
    """Fixture for an HTTP ChromaVectorStore."""

    class VectorStore(ChromaVectorStore):
        index_name = "test"
        client_settings = ChromaSettings(mode="http")

    return VectorStore()


@pytest.fixture
def fixture_ephemeral_client() -> ChromaVectorStore:
    """Fixture for an ephemeral ChromaVectorStore."""

    class VectorStore(ChromaVectorStore):
        index_name = "test"
        client_settings = ChromaSettings(mode="ephemeral")

    return VectorStore()
