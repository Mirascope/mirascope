"""A module for calling Chroma's Client and Collection."""
from contextlib import suppress
from functools import cached_property
from typing import Any, ClassVar, Optional, Union

with suppress(ImportError):
    import weave
from chromadb import Collection, EphemeralClient, HttpClient, PersistentClient
from chromadb.api import ClientAPI

from ..rag.types import Document
from ..rag.vectorstores import BaseVectorStore
from .types import ChromaParams, ChromaQueryResult, ChromaSettings


class ChromaVectorStore(BaseVectorStore):
    """A vectorstore for Chroma.

    Example:

    ```python
    from mirascope.chroma import ChromaSettings, ChromaVectorStore
    from mirascope.openai import OpenAIEmbedder
    from mirascope.rag import TextChunker


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

    def retrieve(
        self, text: Optional[Union[str, list[str]]] = None, **kwargs: Any
    ) -> ChromaQueryResult:
        """Queries the vectorstore for closest match"""
        if text:
            if isinstance(text, str):
                text = [text]
            query_result = self._index.query(query_texts=text, **kwargs)
        else:
            query_result = self._index.query(**kwargs)

        return ChromaQueryResult.model_validate(query_result)

    def add(self, text: Union[str, list[Document]], **kwargs: Any) -> None:
        """Takes unstructured data and upserts into vectorstore"""
        documents: list[Document]
        if isinstance(text, str):
            chunk = self.chunker.chunk
            if self.vectorstore_params.weave and not isinstance(self.chunker, weave.Op):
                chunk = self.vectorstore_params.weave(
                    self.chunker.chunk
                )  # pragma: no cover
            documents = chunk(text)
        else:
            documents = text

        return self._index.upsert(
            ids=[document.id for document in documents],
            documents=[document.text for document in documents],
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
        create_collection = self._client.create_collection
        if self.vectorstore_params.weave is not None:
            create_collection = self.vectorstore_params.weave(
                self._client.create_collection
            )  # pragma: no cover

        return create_collection(
            **vectorstore_params.kwargs(),
            embedding_function=self.embedder,  # type: ignore
        )
