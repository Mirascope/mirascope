"""Tests for the `TextChunker` class."""
from mirascope.rag.chunkers.text_chunker import TextChunker
from mirascope.rag.types import Document


def test_text_chunker_chunk():
    """Test the TextChunker chunk function."""
    text = "This is a test text. " * 100
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)

    chunks = chunker.chunk(text)

    assert len(chunks) == 27
    assert all(isinstance(chunk, Document) for chunk in chunks)
    assert all(chunk.text for chunk in chunks)
    assert all(isinstance(chunk.id, str) for chunk in chunks)

    # Check that chunks are properly split
    assert chunks[0].text == text[:100]
    assert chunks[1].text == text[80:180]

    # Check that chunk IDs are unique
    assert len(set(chunk.id for chunk in chunks)) == len(chunks)
