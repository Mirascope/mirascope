"""A module for calling Chroma's Client and Collection."""

from functools import cached_property
from typing import Any, ClassVar, cast

from chromadb import Collection, EphemeralClient, HttpClient, Metadata, PersistentClient
from chromadb.api import ClientAPI

from ..base.document import Document
from ..base.vectorstores import BaseVectorStore
from .types import ChromaParams, ChromaQueryResult, ChromaSettings


class ChromaVectorStore(BaseVectorStore):
    """A vectorstore for Chroma.

    Example:

    ```python
    from mirascope.beta.rag.chroma import ChromaSettings, ChromaVectorStore
    from mirascope.beta.rag.openai import OpenAIEmbedder
    from mirascope.beta.rag import TextChunker


    class MyStore(ChromaVectorStore):
        embedder = OpenAIEmbedder()
        chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
        index_name = "my-store-0001"
        client_settings = ChromaSettings()

    my_store = MyStore()
    with open(f"{PATH_TO_FILE}") as file:
        data = file.read()
        my_store.add(data)
    documents = my_store.retrieve("my question").documents
    print(documents)
    ```
    """

    vectorstore_params = ChromaParams(get_or_create=True)
    client_settings: ClassVar[ChromaSettings] = ChromaSettings(mode="persistent")
    _provider: ClassVar[str] = "chroma"

    def retrieve(
        self,
        text: str | list[str] | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> ChromaQueryResult:
        """Queries the vectorstore for closest match"""
        if text:
            if isinstance(text, str):
                text = [text]
            query_result = self._index.query(query_texts=text, **kwargs)
        else:
            query_result = self._index.query(**kwargs)

        return ChromaQueryResult.model_validate(query_result)

    def add(self, text: str | list[Document], **kwargs: Any) -> None:  # noqa: ANN401
        """Takes unstructured data and upserts into vectorstore"""
        documents: list[Document]
        if isinstance(text, str):
            chunk = self.chunker.chunk
            documents = chunk(text)
        else:
            documents = text

        return self._index.upsert(
            ids=[document.id for document in documents],
            documents=[document.text for document in documents],
            metadatas=[cast(Metadata, document.metadata) for document in documents],
            **kwargs,
        )

    ############################# PRIVATE PROPERTIES #################################

    @cached_property
    def _client(self) -> ClientAPI:
        if self.client_settings.mode == "persistent":
            return PersistentClient(**self.client_settings.kwargs())
        elif self.client_settings.mode == "http":
            return HttpClient(**self.client_settings.kwargs())
        elif self.client_settings.mode == "ephemeral":
            return EphemeralClient(**self.client_settings.kwargs())

    @cached_property
    def _index(self) -> Collection:
        vectorstore_params = self.vectorstore_params
        if self.index_name:
            vectorstore_params = self.vectorstore_params.model_copy(
                update={"name": self.index_name}
            )

        return self._client.create_collection(
            **vectorstore_params.kwargs(),
            embedding_function=self.embedder,
        )
