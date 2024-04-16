"""Tests for Mirascope PineconeVectorStore class"""
import uuid
from unittest.mock import MagicMock, patch

from pinecone import Index, Pinecone, QueryResponse, ScoredVector

from mirascope.openai.types import EmbeddingResponse
from mirascope.pinecone import PineconeVectorStore
from mirascope.pinecone.types import PineconeQueryResult
from mirascope.rag.types import Document


@patch.object(Pinecone, "__new__", new_callable=MagicMock)
def test_pinecone_vectorstore_add_document(
    mock_pinecone: MagicMock,
    fixture_pinecone: PineconeVectorStore,
):
    """Test the add method of the PineconeVectorStore class with documents as argument"""
    mock_upsert = MagicMock()
    mock_index = MagicMock()
    mock_index.return_value.upsert = mock_upsert
    mock_pinecone.return_value.Index = mock_index
    fixture_pinecone.add([Document(text="foo", id="1")])

    mock_upsert.assert_called_once_with(
        [
            {
                "id": "1",
                "values": [0.1],
                "metadata": {"text": "foo"},
            }
        ]
    )


@patch.object(Pinecone, "__new__", new_callable=MagicMock)
@patch("uuid.uuid4")
def test_pinecone_vectorstore_add_text(
    mock_uuid: MagicMock,
    mock_pinecone: MagicMock,
    fixture_pinecone: PineconeVectorStore,
):
    """Test the add method of the PineconeVectorStore class with string as argument"""
    mock_uuid.return_value = uuid.UUID("12345678-1234-5678-1234-567812345678")
    mock_upsert = MagicMock()
    mock_index = MagicMock()
    mock_index.return_value.upsert = mock_upsert
    mock_pinecone.return_value.Index = mock_index
    fixture_pinecone.add("foo")
    mock_upsert.assert_called_once_with(
        [
            {
                "id": "12345678-1234-5678-1234-567812345678",
                "values": [0.1],
                "metadata": {"text": "foo"},
            }
        ]
    )


@patch.object(Pinecone, "__new__", new_callable=MagicMock)
def test_pinecone_vectorstore_retrieve(
    mock_pinecone: MagicMock,
    fixture_pinecone: PineconeVectorStore,
):
    """Test the retrieve method of the PineconeVectorStore class."""
    mock_query = MagicMock()
    mock_index = MagicMock()
    mock_index.return_value.query = mock_query
    mock_pinecone.return_value.Index = mock_index
    mock_query.return_value = QueryResponse(
        matches=[
            ScoredVector(
                id="1",
                score=0.1,
                values=[0.1],
                metadata={"text": "foo"},
            )
        ]
    )
    fixture_pinecone.retrieve("test_query")
    mock_query.assert_called_once_with(
        vector=[0.1], include_values=True, include_metadata=True, top_k=8
    )


@patch.object(Pinecone, "__new__", new_callable=MagicMock)
def test_pinecone_vectorstore_retrieve_with_handler(
    mock_pinecone: MagicMock,
    fixture_pinecone_with_handlers: PineconeVectorStore,
):
    """Test that handlers are called when adding and retrieving.
    When handle_add_text is called, metadata returns empty object instead of text.
    When handle_retrieve_text is called, it returns a list of strings.
    """
    mock_query = MagicMock()
    mock_upsert = MagicMock()
    mock_index = MagicMock()
    mock_index.return_value.query = mock_query
    mock_index.return_value.upsert = mock_upsert
    mock_pinecone.return_value.Index = mock_index
    mock_query.return_value = QueryResponse(
        matches=[
            ScoredVector(
                id="1",
                score=0.1,
                values=[0.1],
                metadata={"text": "foo"},
            )
        ]
    )
    fixture_pinecone_with_handlers.add([Document(text="foo", id="1")])
    mock_upsert.assert_called_once_with(
        [
            {
                "id": "1",
                "values": [0.1],
                "metadata": {},
            }
        ]
    )
    fixture_pinecone_with_handlers.retrieve("test_query")
    mock_query.assert_called_once_with(
        vector=[0.1], include_values=True, include_metadata=True, top_k=8
    )
