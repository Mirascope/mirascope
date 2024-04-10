import uuid

from mirascope.chroma import ChromaSettings, ChromaVectorStore
from mirascope.openai import OpenAIEmbedder
from mirascope.rag import BaseChunker, Document

prev_revision_id = None
revision_id = "0001"


class MyChunker(BaseChunker):
    chunk_size: int
    chunk_overlap: int

    def chunk(self, text: str) -> list[Document]:
        chunks: list[Document] = []
        start: int = 0
        while start < len(text):
            end: int = min(start + self.chunk_size, len(text))
            chunks.append(Document(text=text[start:end], id=str(uuid.uuid4())))
            start += self.chunk_size - self.chunk_overlap
        return chunks


class WikipediaStore(ChromaVectorStore):
    embedder = OpenAIEmbedder()
    chunker = MyChunker(chunk_size=1000, chunk_overlap=200)
    index_name = "wikipedia-0001"
    client_settings = ChromaSettings()
