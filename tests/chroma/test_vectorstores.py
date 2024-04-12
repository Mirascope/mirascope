"""Tests for Mirascope ChromaVectorStore class"""
import uuid
from unittest.mock import MagicMock, patch

import pytest

from mirascope.chroma import ChromaVectorStore
from mirascope.chroma.types import ChromaQueryResult
from mirascope.rag.types import Document


@patch("chromadb.api.models.Collection.Collection.upsert")
def test_chroma_vectorstore_add_document(
    mock_upsert: MagicMock,
    fixture_ephemeral_client: ChromaVectorStore,
):
    """Test the add method of the ChromaVectorStore class with documents as argument"""
    mock_upsert.return_value = None
    fixture_ephemeral_client.add([Document(text="foo", id="1")])
    mock_upsert.assert_called_once_with(ids=["1"], documents=["foo"])


@patch("chromadb.api.models.Collection.Collection.upsert")
@patch("uuid.uuid4")
def test_chroma_vectorstore_add_text(
    mock_uuid: MagicMock,
    mock_upsert: MagicMock,
    fixture_ephemeral_client: ChromaVectorStore,
):
    """Test the add method of the ChromaVectorStore class with string as argument"""
    mock_uuid.return_value = uuid.UUID("12345678-1234-5678-1234-567812345678")
    mock_upsert.return_value = None
    fixture_ephemeral_client.add("foo")
    mock_upsert.assert_called_once_with(
        ids=["12345678-1234-5678-1234-567812345678"], documents=["foo"]
    )


@pytest.mark.parametrize(
    "query_texts,",
    ["test_query", {"query_texts": ["test_query"]}],
)
@patch("chromadb.api.models.Collection.Collection.query")
def test_chroma_vectorstore_retrieve(
    mock_query: MagicMock,
    query_texts: str | dict,
    fixture_ephemeral_client: ChromaVectorStore,
):
    """Test the retrieve method of the ChromaVectorStore class."""
    mock_query.return_value = ChromaQueryResult(ids=[["1"]])
    if isinstance(query_texts, str):
        fixture_ephemeral_client.retrieve(query_texts)
    else:
        fixture_ephemeral_client.retrieve(**query_texts)
    mock_query.assert_called_once_with(query_texts=["test_query"])


@patch("mirascope.chroma.vectorstores.PersistentClient", new_callable=MagicMock)
def test_chroma_vectorstore_persistent_mode(
    mock_chroma_client: MagicMock, fixture_persistent_client: ChromaVectorStore
):
    """Test the _client property with mode=persistent of the ChromaVectorStore class."""
    fixture_persistent_client._client
    mock_chroma_client.assert_called_once()


@patch("mirascope.chroma.vectorstores.EphemeralClient", new_callable=MagicMock)
def test_chroma_vectorstore_ephemeral_mode(
    mock_chroma_client: MagicMock, fixture_ephemeral_client: ChromaVectorStore
):
    """Test the _client property with mode=ephemeral of the ChromaVectorStore class."""
    fixture_ephemeral_client._client
    mock_chroma_client.assert_called_once()


@patch("mirascope.chroma.vectorstores.HttpClient", new_callable=MagicMock)
def test_chroma_vectorstore_http_mode(
    mock_chroma_client: MagicMock, fixture_http_client: ChromaVectorStore
):
    """Test the _client property with mode=http of the ChromaVectorStore class."""
    fixture_http_client._client
    mock_chroma_client.assert_called_once()
