"""Tests for Mirascope AstraVectorStore class"""
import pytest
from unittest.mock import patch, MagicMock
from mirascope.astra.vectorstores import AstraVectorStore
from mirascope.astra.types import AstraQueryResult
from mirascope.rag.types import Document

@patch("astra.db.Collection.insert_one")  # Assuming the insert method in your DB collection
def test_astra_vectorstore_add_document(mock_insert: MagicMock):
    store = AstraVectorStore()
    document = Document(text="example", id="123")  # Adjust with actual constructors
    store.add(document)
    mock_insert.assert_called_once_with({"id": "123", "text": "example"})  # Adjust fields as necessary

@patch("astra.db.Collection.insert_one")  # Adjust the path based on actual implementation
def test_astra_vectorstore_add_document(mock_insert: MagicMock):
    store = AstraVectorStore()
    document = Document(text="example text", id="1")  # Create a test document
    store.add([document])  # Assuming add method can take a list of documents
    mock_insert.assert_called_once_with({"text": "example text", "id": "1"})

@patch("astra.db.Collection.insert_one")
@patch("uuid.uuid4", return_value=uuid.UUID("12345678-1234-5678-1234-567812345678"))
def test_astra_vectorstore_add_text(mock_uuid: MagicMock, mock_insert: MagicMock):
    store = AstraVectorStore()
    store.add("example text")
    mock_insert.assert_called_once_with({"text": "example text", "id": "12345678-1234-5678-1234-567812345678"})

@patch("astra.db.Collection.find")
def test_astra_vectorstore_retrieve(mock_find: MagicMock):
    mock_find.return_value = AstraQueryResult(documents=[["1", "example text"]])
    store = AstraVectorStore()
    result = store.retrieve("example text")
    mock_find.assert_called_once_with({"text": "example text"})
    assert result.documents == [["1", "example text"]]