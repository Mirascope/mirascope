"""Configurations for Mirascope PineconeVectorStore module tests"""


import pytest
from cohere.types import (
    ApiMeta,
    ApiMetaApiVersion,
    ApiMetaBilledUnits,
    EmbedByTypeResponseEmbeddings,
    EmbedResponse_EmbeddingsByType,
)
from openai.types.create_embedding_response import CreateEmbeddingResponse, Usage
from openai.types.embedding import Embedding

from mirascope.cohere.types import CohereEmbeddingResponse
from mirascope.openai.types import OpenAIEmbeddingResponse
from mirascope.pinecone import PineconeSettings, PineconeVectorStore
from mirascope.pinecone.types import PineconePodParams
from mirascope.rag import BaseEmbedder
from mirascope.rag.types import Document

openai_embedding_response = OpenAIEmbeddingResponse(
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
cohere_embedding_response = CohereEmbeddingResponse(
    response=EmbedResponse_EmbeddingsByType(
        id="test",
        embeddings=EmbedByTypeResponseEmbeddings(int8=None),
        texts=["test"],
        meta=ApiMeta(
            api_version=ApiMetaApiVersion(version="test"),
            billed_units=ApiMetaBilledUnits(
                output_tokens=1,
                input_tokens=1,
            ),
        ),
    ),
    start_time=0,
    end_time=0,
)


class TestOpenAIEmbedder(BaseEmbedder):
    def embed(self, input: list[str]) -> OpenAIEmbeddingResponse:
        return openai_embedding_response

    async def embed_async(self, input: list[str]) -> OpenAIEmbeddingResponse:
        return openai_embedding_response  # pragma: no cover

    def __call__(self, input: str) -> list[float]:
        return [1, 2, 3]


class TestCohereEmbedder(BaseEmbedder):
    def embed(self, input: list[str]) -> CohereEmbeddingResponse:
        return cohere_embedding_response

    async def embed_async(self, input: list[str]) -> CohereEmbeddingResponse:
        return cohere_embedding_response  # pragma: no cover

    def __call__(self, input: str) -> list[float]:
        return [1, 2, 3]


@pytest.fixture
def fixture_pinecone_with_openai() -> PineconeVectorStore:
    """Fixture for PineconeVectorStore with OpenAIEmbedder."""

    class VectorStore(PineconeVectorStore):
        api_key = "test key"
        index_name = "test"
        embedder = TestOpenAIEmbedder()
        client_settings = PineconeSettings()

    vectorstore = VectorStore()
    vectorstore.embedder("foo")
    return vectorstore


@pytest.fixture
def fixture_pinecone_with_cohere() -> PineconeVectorStore:
    """Fixture for PineconeVectorStore with CohereEmbedder."""

    class VectorStore(PineconeVectorStore):
        api_key = "test key"
        index_name = "test"
        embedder = TestCohereEmbedder()
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
        embedder = TestOpenAIEmbedder()
        client_settings = PineconeSettings()
        vectorstore_params = PineconePodParams(environment="test")

    vectorstore = VectorStore()
    return vectorstore
