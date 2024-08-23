"""A module for calling Chroma's Client and Collection."""

from collections.abc import Callable
from functools import cached_property
from typing import Any, ClassVar

from pinecone import Index, Pinecone, QueryResponse

from ..base.document import Document
from ..base.embedding_response import BaseEmbeddingResponse
from ..base.vectorstores import BaseVectorStore
from .types import (
    PineconePodParams,
    PineconeQueryResult,
    PineconeServerlessParams,
    PineconeSettings,
)


class PineconeVectorStore(BaseVectorStore):
    """A vectorstore for Pinecone.

    Example:

    ```python
    from mirascope.beta.rag.pinecone import (
        PineconeServerlessParams,
        PineconeSettings,
        PineconeVectorStore,
    )
    from mirascope.beta.rag.openai import OpenAIEmbedder
    from mirascope.beta.rag import TextChunker


    class MyStore(PineconeVectorStore):
        embedder = OpenAIEmbedder(dimensions=1536)
        chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
        index_name = "my-store-0001"
        api_key = settings.pinecone_api_key
        client_settings = PineconeSettings()
        vectorstore_params = PineconeServerlessParams(
            cloud="aws",
            region="us-west-2",
        )

    my_store = MyStore()
    with open(f"{PATH_TO_FILE}") as file:
        data = file.read()
        my_store.add(data)
    documents = my_store.retrieve("my question").documents
    print(documents)
    ```
    """

    handle_add_text: Callable[[list[Document]], None] | None = None
    handle_retrieve_text: Callable[[list[float]], list[str]] | None = None

    vectorstore_params: ClassVar[PineconePodParams | PineconeServerlessParams] = (
        PineconeServerlessParams(cloud="aws", region="us-east-1")
    )
    client_settings: ClassVar[PineconeSettings] = PineconeSettings()
    _provider: ClassVar[str] = "pinecone"

    def retrieve(self, text: str, **kwargs: Any) -> PineconeQueryResult:  # noqa: ANN401
        """Queries the vectorstore for closest match"""
        embed = self.embedder.embed
        text_embedding: BaseEmbeddingResponse = embed([text])
        if "top_k" not in kwargs:
            kwargs["top_k"] = 8
        if text_embedding.embeddings is None:
            raise ValueError("Embedding is None")
        query_result: QueryResponse = self._index.query(
            vector=text_embedding.embeddings[0],
            **{"include_metadata": True, "include_values": True, **kwargs},
        )
        ids: list[str] = []
        scores: list[float] = []
        documents: list[str] = []
        embeddings: list[list[float]] = []
        for match in query_result.matches:
            ids.append(match.id)
            scores.append(match.score)
            documents.append(
                self.handle_retrieve_text([match.values])[0]
                if self.handle_retrieve_text
                else match.metadata["text"]
            )
            embeddings.append(match.values)

        return PineconeQueryResult(
            ids=ids,
            scores=scores,
            documents=documents,
            embeddings=embeddings,
        )

    def add(
        self,
        text: str | list[Document],
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Takes unstructured data and upserts into vectorstore"""
        documents: list[Document]
        if isinstance(text, str):
            chunk = self.chunker.chunk
            documents = chunk(text)
        else:
            documents = text
        inputs = [document.text for document in documents]
        embed = self.embedder.embed
        embedding_repsonse: BaseEmbeddingResponse = embed(inputs)
        if self.handle_add_text:
            self.handle_add_text(documents)
        if embedding_repsonse.embeddings is None:
            raise ValueError("Embedding is None")
        vectors = []
        for i, embedding in enumerate(embedding_repsonse.embeddings):
            if documents[i] is not None:
                metadata = documents[i].metadata or {}
                metadata_text = (
                    {"text": documents[i].text}
                    if documents[i].text and not self.handle_add_text
                    else {}
                )
                vectors.append(
                    {
                        "id": documents[i].id,
                        "values": embedding,
                        "metadata": {**metadata, **metadata_text},
                    }
                )
        return self._index.upsert(vectors, **kwargs)

    ############################# PRIVATE PROPERTIES #################################

    @cached_property
    def _client(self) -> Pinecone:
        return Pinecone(api_key=self.api_key, **self.client_settings.kwargs())

    @cached_property
    def _index(self) -> Index:
        if self.index_name not in self._client.list_indexes().names():
            self._client.create_index(
                name=self.index_name,
                dimension=self.embedder.dimensions,
                **self.vectorstore_params.kwargs(),
            )
        return self._client.Index(self.index_name)
