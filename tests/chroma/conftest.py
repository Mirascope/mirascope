"""Configuration for the Mirascope chroma module tests."""

import pytest

from mirascope.chroma.types import ChromaSettings
from mirascope.chroma.vectorstores import ChromaVectorStore
from mirascope.rag import BaseEmbedder


class MyEmbedder(BaseEmbedder):
    def embed(self, input: list[str]) -> list[str]:
        return input

    async def embed_async(self, input: list[str]) -> list[str]:
        return input  # pragma: no cover

    def __call__(self, input: str) -> list[float]:
        return [1, 2, 3]


@pytest.fixture
def fixture_ephemeral_client() -> ChromaVectorStore:
    """Fixture for an ephemeral ChromaVectorStore."""

    class VectorStore(ChromaVectorStore):
        index_name = "test"
        client_settings = ChromaSettings(mode="ephemeral")
        embedder = MyEmbedder()

    return VectorStore()


@pytest.fixture
def fixture_persistent_client() -> ChromaVectorStore:
    """Fixture for a persistent ChromaVectorStore."""

    class VectorStore(ChromaVectorStore):
        index_name = "test"
        embedder = MyEmbedder()
        client_settings = ChromaSettings(mode="persistent")

    vectorstore = VectorStore()
    vectorstore.embedder.embed(["foo"])
    vectorstore.embedder("foo")
    return VectorStore()


@pytest.fixture
def fixture_http_client() -> ChromaVectorStore:
    """Fixture for an HTTP ChromaVectorStore."""

    class VectorStore(ChromaVectorStore):
        index_name = "test"
        embedder = MyEmbedder()
        client_settings = ChromaSettings(mode="http")

    return VectorStore()
