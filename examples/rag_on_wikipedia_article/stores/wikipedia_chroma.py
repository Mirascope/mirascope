"""Chroma store for Wikipedia articles."""
from mirascope.chroma import ChromaSettings, ChromaVectorStore
from mirascope.logfire import with_logfire
from mirascope.openai import OpenAIEmbedder
from mirascope.rag import TextChunker


@with_logfire
class WikipediaStore(ChromaVectorStore):
    embedder = OpenAIEmbedder()
    chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
    index_name = "wikipedia-0001"
    client_settings = ChromaSettings()
