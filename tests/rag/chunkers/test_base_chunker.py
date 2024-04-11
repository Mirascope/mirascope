"""Tests for the `BaseChunker` class."""
from unittest.mock import patch

from mirascope.rag.chunkers.base import BaseChunker
from mirascope.rag.types import Document


@patch.multiple(BaseChunker, __abstractmethods__=set())
def test_base_chunker() -> None:
    """Tests the `BaseChunker` interface."""

    class MyChunker(BaseChunker):
        chunk_size: int
        chunk_overlap: int

        def chunk(self, text: str) -> list[Document]:
            return [Document(id="1", text=text, metadata={"foo": "bar"})]

    my_chunker = MyChunker(chunk_overlap=10, chunk_size=100)
    documents = my_chunker.chunk("test")
    for document in documents:
        assert isinstance(document, Document)
    assert isinstance(my_chunker, BaseChunker)
