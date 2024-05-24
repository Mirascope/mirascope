"""Tests for the `CohereEmbedder` class."""

from typing import Literal, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from cohere.types import EmbedResponse_EmbeddingsFloats
from pytest import FixtureRequest

from mirascope.cohere.embedders import CohereEmbedder
from mirascope.cohere.types import CohereEmbeddingResponse


@patch(
    "cohere.client.Client.embed",
    new_callable=MagicMock,
)
def test_cohere_embedder_embed(
    mock_embed: MagicMock,
    fixture_cohere_test_embedder: CohereEmbedder,
    fixture_cohere_embeddings: EmbedResponse_EmbeddingsFloats,
):
    """Tests `CohereEmbedder.embed` returns the expected response when called."""
    mock_embed.return_value = fixture_cohere_embeddings

    text = "This is a test sentence."
    embedding = fixture_cohere_test_embedder.embed([text])
    assert isinstance(embedding, CohereEmbeddingResponse)


@patch(
    "cohere.client.AsyncClient.embed",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_cohere_embedder_embed_async(
    mock_embed: AsyncMock,
    fixture_cohere_test_embedder: CohereEmbedder,
    fixture_cohere_embeddings: EmbedResponse_EmbeddingsFloats,
) -> None:
    """Tests `CohereEmbedder.embed_async` returns the expected response when called."""
    mock_embed.return_value = fixture_cohere_embeddings

    text = "This is a test sentence."
    response = await fixture_cohere_test_embedder.embed_async([text])
    assert isinstance(response, CohereEmbeddingResponse)


@patch(
    "cohere.client.Client.embed",
    new_callable=MagicMock,
)
@pytest.mark.parametrize(
    "cohere_embeddings,embedding_type,instance",
    [
        ("fixture_cohere_embeddings", None, list),
        ("fixture_cohere_embeddings_by_type_float", "float", list),
        ("fixture_cohere_embeddings_by_type_int8", "int8", list),
        ("fixture_cohere_embeddings_by_type_uint8", "uint8", list),
        ("fixture_cohere_embeddings_by_type_binary", "binary", list),
        ("fixture_cohere_embeddings_by_type_ubinary", "ubinary", list),
        ("fixture_cohere_embeddings_by_type_no_data", "int8", type(None)),
    ],
)
def test_cohere_embedder_call(
    mock_embed: MagicMock,
    cohere_embeddings: str,
    embedding_type: Optional[Literal["float", "int8", "uint8", "binary", "ubinary"]],
    instance: type,
    fixture_cohere_test_embedder: CohereEmbedder,
    request: FixtureRequest,
):
    """Tests `CohereEmbedder.__call__` returns the expected response when called."""
    mock_embed.return_value = request.getfixturevalue(cohere_embeddings)
    text = "This is a test sentence."
    fixture_cohere_test_embedder.embedding_params.embedding_types = (
        [embedding_type] if embedding_type else None
    )
    embedding = fixture_cohere_test_embedder([text])
    assert isinstance(embedding, instance)
