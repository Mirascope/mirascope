"""Chroma store for Wikipedia articles."""

from mirascope.cohere import CohereEmbedder
from mirascope.pinecone import (
    PineconeServerlessParams,
    PineconeSettings,
    PineconeVectorStore,
)
from mirascope.rag import TextChunker


class WikipediaStore(PineconeVectorStore):
    embedder = CohereEmbedder()
    chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
    index_name = "wikipedia-cohere-0001"
    client_settings = PineconeSettings()
    vectorstore_params = PineconeServerlessParams(cloud="aws", region="us-east-1")
