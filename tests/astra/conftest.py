"""Configuration for the Mirascope astra module tests."""
"""Configuration for the Astra module tests."""

import pytest
from astra.types import AstraSettings
from astra.vectorstores import AstraVectorStore
from some_module import BaseEmbedder  # Update the import according to your actual embedder location

class MyEmbedder(BaseEmbedder):
    def embed(self, input: list[str]) -> list[str]:
        return input

    async def embed_async(self, input: list[str]) -> list[str]:
        return input  # pragma: no cover

    def __call__(self, input: str) -> list[float]:
        return [1, 2, 3]

@pytest.fixture
def fixture_persistent_client() -> AstraVectorStore:
    """Fixture for a persistent AstraVectorStore."""

    class VectorStore(AstraVectorStore):
        index_name = "test"
        embedder = MyEmbedder()
        client_settings = AstraSettings(mode="persistent")

    vectorstore = VectorStore()
    vectorstore.embedder.embed(["foo"])
    vectorstore.embedder("foo")
    return VectorStore()

@pytest.fixture
def fixture_http_client() -> AstraVectorStore:
    """Fixture for an HTTP AstraVectorStore."""

    class VectorStore(AstraVectorStore):
        index_name = "test"
        embedder = MyEmbedder()
        client_settings = AstraSettings(mode="http")

    return VectorStore()

@pytest.fixture
def fixture_ephemeral_client() -> AstraVectorStore:
    """Fixture for an ephemeral AstraVectorStore."""

    class VectorStore(AstraVectorStore):
        index_name = "test"
        client_settings = AstraSettings(mode="ephemeral")
        embedder = MyEmbedder()

    return VectorStore()
