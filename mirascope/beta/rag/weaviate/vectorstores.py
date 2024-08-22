from functools import cached_property
from typing import Any, ClassVar

import weaviate
import weaviate.classes as wvc
from weaviate import WeaviateClient
from weaviate.collections.collection import Collection

from ..base.document import Document
from ..base.vectorstores import BaseVectorStore
from .types import (
    WeaviateParams,
    WeaviateQueryResult,
    WeaviateSettings,
)


class WeaviateVectorStore(BaseVectorStore):
    """A vectorstore for Weaviate.

    Example:

    ```python
    from mirascope.beta.rag.weaviate.types import WeaviateSettings, WeaviateParams
    from mirascope.beta.rag.weaviate import WeaviateVectorStore
    from mirascope.beta.rag import TextChunker


    class MyStore(WeaviateVectorStore):
        chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
        index_name = "my-store-0001"
        client_settings = WeaviateSettings()

    my_store = MyStore()
    with open(f"{PATH_TO_FILE}") as file:
        data = file.read()
        my_store.add(data)
    properties = my_store.retrieve("my question").properties
    print(documents)
    """

    _provider: ClassVar[str] = "weaviate"
    vectorstore_params = WeaviateParams()
    client_settings: ClassVar[WeaviateSettings] = WeaviateSettings()

    def add(self, text: str | list[Document], **kwargs: Any) -> None:  # noqa: ANN401
        """Takes unstructured data and inserts into vectorstore"""
        documents: list[Document]
        if isinstance(text, str):
            chunk = self.chunker.chunk
            documents = chunk(text)
        else:
            documents = text

        if len(documents) < 2:
            return self._index.data.insert(
                properties={"text": documents[0].text}, uuid=documents[0].id, **kwargs
            )

        data_objects = []
        for document in documents:
            data_object = wvc.data.DataObject(
                properties={"text": document.text}, uuid=document.id
            )
            data_objects.append(data_object)

        return self._index.data.insert_many(data_objects)

    def retrieve(self, text: str, **kwargs: Any) -> WeaviateQueryResult:  # noqa: ANN401
        """Queries the vectorstore for closest match"""
        query_result = self._index.query.near_text(query=text, **kwargs)
        result = query_result.objects[0]

        return WeaviateQueryResult.from_response(result)

    def close_connection(self) -> None:
        self._client.close()

    ############################# PRIVATE PROPERTIES #################################

    @cached_property
    def _client(self) -> WeaviateClient:
        if self.client_settings.mode == "local":
            return weaviate.connect_to_local(**self.client_settings.kwargs())
        elif self.client_settings.mode == "embedded":
            return weaviate.connect_to_embedded(**self.client_settings.kwargs())
        elif self.client_settings.mode == "cloud":
            return weaviate.connect_to_weaviate_cloud(**self.client_settings.kwargs())
        elif self.client_settings.mode == "custom":
            return weaviate.connect_to_custom(**self.client_settings.kwargs())

    @cached_property
    def _index(self) -> Collection:
        vectorstore_params = self.vectorstore_params

        if self.index_name:
            vectorstore_params = self.vectorstore_params.model_copy(
                update={"name": self.index_name}
            )
        if self._client.collections.exists(self.index_name):
            return self._client.collections.get(self.index_name)

        return self._client.collections.create(**vectorstore_params.kwargs())
