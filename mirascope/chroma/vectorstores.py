from typing import Any, ClassVar, Optional, Union

from chromadb import Client, Collection
from chromadb import Settings as ClientSettings
from chromadb.api import ClientAPI

from mirascope.base.chunkers import BaseChunker, Document
from mirascope.base.utils import convert_function_to_chunker
from mirascope.base.vectorstores import BaseVectorStore
from mirascope.chroma.types import ChromaParams, ChromaQueryResult


class ChromaVectorStore(BaseVectorStore):
    """A vectorstore for Chroma."""

    vectorstore_params = ChromaParams(get_or_create=True)
    client_settings: ClassVar[ClientSettings] = ClientSettings()

    def get_documents(
        self, text: Optional[Union[str, list[str]]] = None, **kwargs: Any
    ) -> Optional[list[list[str]]]:
        return self._get_query_results(text, **kwargs).documents

    def add_documents(self, text: Union[str, list[Document]], **kwargs: Any) -> None:
        """Takes unstructured data and upserts into vectorstore"""
        documents: list[Document]
        if isinstance(text, str):
            if isinstance(self.chunker, BaseChunker):
                chunker = self.chunker
            else:
                chunker = convert_function_to_chunker(self.chunker, BaseChunker)()

            documents = chunker.chunk(text)
        else:
            documents = text

        return self._index.upsert(
            ids=[document.id for document in documents],
            documents=[document.text for document in documents],
            **kwargs,
        )

    ############################## PRIVATE METHODS ###################################

    @property
    def _client(self) -> ClientAPI:
        return Client(self.client_settings)

    @property
    def _index(self) -> Collection:
        vectorstore_params = self.vectorstore_params
        if self.index_name:
            vectorstore_params = self.vectorstore_params.model_copy(
                update={"name": self.index_name}
            )
        return self._client.create_collection(
            **vectorstore_params.kwargs(),
            embedding_function=self.embedder,  # type: ignore
        )

    def _get_query_results(
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
