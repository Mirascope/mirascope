"""Tests for the `OpenAIEmbedder` class."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai.types.create_embedding_response import CreateEmbeddingResponse

from mirascope.openai import OpenAIEmbedder


@patch(
    "openai.resources.embeddings.Embeddings.create",
    new_callable=MagicMock,
)
def test_openai_embedder_embed(
    mock_create: MagicMock,
    fixture_openai_test_embedder: OpenAIEmbedder,
    fixture_embeddings: CreateEmbeddingResponse,
):
    """Tests `OpenAIEmbedder.embed` returns the expected response when called."""
    mock_create.return_value = fixture_embeddings

    text = "This is a test sentence."
    embedding = fixture_openai_test_embedder.embed([text])
    assert isinstance(embedding, list)


@patch(
    "openai.resources.embeddings.AsyncEmbeddings.create",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_openai_embedder_embed_async(
    mock_create: AsyncMock,
    fixture_openai_test_embedder: OpenAIEmbedder,
    fixture_embeddings: CreateEmbeddingResponse,
) -> None:
    """Tests `OpenAIEmbedder.embed_async` returns the expected response when called."""
    mock_create.return_value = fixture_embeddings

    text = "This is a test sentence."
    response = await fixture_openai_test_embedder.embed_async([text])
    assert isinstance(response, list)


@patch(
    "openai.resources.embeddings.Embeddings.create",
    new_callable=MagicMock,
)
def test_openai_embedder_call(
    mock_create: MagicMock,
    fixture_openai_test_embedder: OpenAIEmbedder,
    fixture_embeddings: CreateEmbeddingResponse,
):
    """Tests `OpenAIEmbedder.__call__` returns the expected response when called."""
    mock_create.return_value = fixture_embeddings
    text = "This is a test sentence."
    embedding = fixture_openai_test_embedder([text])
    assert isinstance(embedding, list)
