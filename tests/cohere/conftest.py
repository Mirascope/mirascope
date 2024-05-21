"""Fixtures for Mirascope's Cohere module tests."""
from typing import Type

import pytest
from cohere.types import (
    ApiMeta,
    ApiMetaBilledUnits,
    EmbedByTypeResponseEmbeddings,
    EmbedResponse_EmbeddingsByType,
    EmbedResponse_EmbeddingsFloats,
    NonStreamedChatResponse,
    ToolCall,
)

from mirascope.cohere.embedders import CohereEmbedder
from mirascope.cohere.tools import CohereTool
from mirascope.cohere.types import CohereEmbeddingParams


@pytest.fixture()
def fixture_cohere_embeddings() -> EmbedResponse_EmbeddingsFloats:
    """Returns a Cohere embeddings response with embedding_types None."""
    return EmbedResponse_EmbeddingsFloats(
        id="test",
        embeddings=[
            [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        ],
        texts=["test"],
        meta=ApiMeta(billed_units=ApiMetaBilledUnits(input_tokens=1, output_tokens=1)),
    )


@pytest.fixture()
def fixture_cohere_embeddings_by_type_float() -> EmbedResponse_EmbeddingsByType:
    """Returns a Cohere embeddings response with embedding_types float."""
    return EmbedResponse_EmbeddingsByType(
        id="test",
        embeddings=EmbedByTypeResponseEmbeddings(
            float_=[  # type: ignore
                [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            ]
        ),
        texts=["test"],
        meta=ApiMeta(billed_units=ApiMetaBilledUnits(input_tokens=1, output_tokens=1)),
    )


@pytest.fixture()
def fixture_cohere_embeddings_by_type_int8() -> EmbedResponse_EmbeddingsByType:
    """Returns a Cohere embeddings response with embedding_types int8."""
    return EmbedResponse_EmbeddingsByType(
        id="test",
        embeddings=EmbedByTypeResponseEmbeddings(
            int8=[
                [-127, -126, -125, -124, -123, -122, -121, -120, -119],
            ]
        ),
        texts=["test"],
        meta=ApiMeta(billed_units=ApiMetaBilledUnits(input_tokens=1, output_tokens=1)),
    )


@pytest.fixture()
def fixture_cohere_embeddings_by_type_uint8() -> EmbedResponse_EmbeddingsByType:
    """Returns a Cohere embeddings response with embedding_types uint8."""
    return EmbedResponse_EmbeddingsByType(
        id="test",
        embeddings=EmbedByTypeResponseEmbeddings(
            uint8=[
                [1, 2, 3, 4, 5, 6, 7, 8, 9],
            ]
        ),
        texts=["test"],
        meta=ApiMeta(billed_units=ApiMetaBilledUnits(input_tokens=1, output_tokens=1)),
    )


@pytest.fixture()
def fixture_cohere_embeddings_by_type_binary() -> EmbedResponse_EmbeddingsByType:
    """Returns a Cohere embeddings response with embedding_types binary."""
    return EmbedResponse_EmbeddingsByType(
        id="test",
        embeddings=EmbedByTypeResponseEmbeddings(
            binary=[
                [-127, -126, -125, -124, -123, -122, -121, -120, -119],
            ]
        ),
        texts=["test"],
        meta=ApiMeta(billed_units=ApiMetaBilledUnits(input_tokens=1, output_tokens=1)),
    )


@pytest.fixture()
def fixture_cohere_embeddings_by_type_ubinary() -> EmbedResponse_EmbeddingsByType:
    """Returns a Cohere embeddings response with embedding_types ubinary."""
    return EmbedResponse_EmbeddingsByType(
        id="test",
        embeddings=EmbedByTypeResponseEmbeddings(
            ubinary=[
                [1, 2, 3, 4, 5, 6, 7, 8, 9],
            ]
        ),
        texts=["test"],
        meta=ApiMeta(billed_units=ApiMetaBilledUnits(input_tokens=1, output_tokens=1)),
    )


@pytest.fixture()
def fixture_cohere_embeddings_by_type_no_data() -> EmbedResponse_EmbeddingsByType:
    """Returns a Cohere embeddings response with embedding_type float with no data."""
    return EmbedResponse_EmbeddingsByType(
        id="test",
        embeddings=EmbedByTypeResponseEmbeddings(
            float_=None  # type: ignore
        ),
        texts=["test"],
        meta=ApiMeta(billed_units=ApiMetaBilledUnits(input_tokens=1, output_tokens=1)),
    )


@pytest.fixture()
def fixture_cohere_test_embedder():
    """Returns an `CohereEmbedding` instance."""

    class TestEmbedder(CohereEmbedder):
        api_key = "test"
        embedding_params = CohereEmbeddingParams(model="test_model")

    return TestEmbedder()
