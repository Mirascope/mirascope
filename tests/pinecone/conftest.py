"""Configurations for Mirascope PineconeVectorStore module tests"""

from unittest.mock import MagicMock, patch

import pytest
from openai.types.create_embedding_response import CreateEmbeddingResponse, Usage
from openai.types.embedding import Embedding
from pinecone.data import Index

from mirascope.openai.types import EmbeddingResponse
from mirascope.pinecone import PineconeSettings, PineconeVectorStore
from mirascope.pinecone.types import PineconePodParams
from mirascope.rag import BaseEmbedder
from mirascope.rag.types import Document

embedding_response = [
    EmbeddingResponse(
        response=CreateEmbeddingResponse(
            data=[
                Embedding(
                    embedding=[0.1],
                    index=0,
                    object="embedding",
                )
            ],
            model="test_model",
            object="list",
            usage=Usage(
                prompt_tokens=1,
                total_tokens=1,
            ),
        ),
        start_time=0,
        end_time=0,
    )
]


class TestEmbedder(BaseEmbedder):
    def embed(self, input: list[str]) -> list[EmbeddingResponse]:
        return embedding_response

    async def embed_async(self, input: list[str]) -> list[EmbeddingResponse]:
        return embedding_response  # pragma: no cover

    def __call__(self, input: str) -> list[float]:
        return [1, 2, 3]


@pytest.fixture
def fixture_pinecone() -> PineconeVectorStore:
    """Fixture for PineconeVectorStore."""

    class VectorStore(PineconeVectorStore):
        api_key = "test key"
        index_name = "test"
        embedder = TestEmbedder()
        client_settings = PineconeSettings()

    vectorstore = VectorStore()
    vectorstore.embedder("foo")
    return vectorstore


def handle_add_text(text: list[Document]) -> None:
    pass


def handle_retrieve_text(embedding: list[float]) -> list[str]:
    return ["foo"]


@pytest.fixture
def fixture_pinecone_with_handlers() -> PineconeVectorStore:
    """Fixture for PineconeVectorStore with handlers."""

    class VectorStore(PineconeVectorStore):
        handle_add_text = handle_add_text
        handle_retrieve_text = handle_retrieve_text
        api_key = "test key"
        index_name = "test"
        embedder = TestEmbedder()
        client_settings = PineconeSettings()
        vectorstore_params = PineconePodParams(environment="test")

    vectorstore = VectorStore()
    return vectorstore
