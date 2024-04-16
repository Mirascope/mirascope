"""Pinecone store for Wikipedia articles."""
from examples.rag_on_wikipedia_article.rag_config import settings
from mirascope.openai import OpenAIEmbedder
from mirascope.pinecone import (
    PineconeServerlessParams,
    PineconeSettings,
    PineconeVectorStore,
)
from mirascope.rag.chunkers import TextChunker


class WikipediaStore(PineconeVectorStore):
    embedder = OpenAIEmbedder(dimensions=1536)
    chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
    index_name = "wikipedia-0001"
    api_key = settings.pinecone_api_key
    client_settings = PineconeSettings()
    vectorstore_params = PineconeServerlessParams(
        cloud="aws",
        region="us-west-2",
    )
