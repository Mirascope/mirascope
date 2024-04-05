from typing import Any, ClassVar

from chromadb import Client, Collection, QueryResult
from chromadb import Settings as ClientSettings

from mirascope.base.vectorstores import BaseVectorStore
from mirascope.chroma.types import ChromaParams


class ChromaVectorStore(BaseVectorStore):
    """A vectorstore for Chroma."""

    vectorstore_params: ClassVar[ChromaParams] = ChromaParams(get_or_create=True)
    client_settings: ClassVar[ClientSettings] = ClientSettings()

    @property
    def _client(self) -> Client:
        return Client(self.client_settings)

    @property
    def _index(self) -> Collection:
        vectorstore_params = self.vectorstore_params
        if self.index_name:
            vectorstore_params = self.vectorstore_params.model_copy(
                update={"name": self.index_name}
            )
        return self._client.create_collection(**vectorstore_params.kwargs())

    def get_documents(self, **kwargs: Any) -> list[QueryResult]:
        """Queries the vectorstore for closest match"""
        return self._index.query(**kwargs)

    def add_documents(self, **kwargs: Any) -> dict:
        """Takes unstructured data and upserts into vectorstore"""
        return self._index.upsert(**kwargs)
