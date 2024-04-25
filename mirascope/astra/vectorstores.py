from contextlib import suppress
from functools import cached_property
from typing import Any, ClassVar, Optional, Union

from astrapy.db import AstraDB
from ..rag.types import Document
from ..rag.vectorstores import BaseVectorStore
from .types import AstraParams, AstraQueryResult, AstraSettings

class AstraVectorStore(BaseVectorStore):
    """A vector store for AstraDB.
    
    Example:
        from your_module import AstraSettings, AstraVectorStore
        from mirascope.openai import OpenAIEmbedder
        from mirascope.rag import TextChunker

        class MyStore(AstraVectorStore):
            embedder = OpenAIEmbedder()
            chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
            collection_name = "my-store-0001"
            client_settings = AstraSettings()

        my_store = MyStore()
        with open(f"{PATH_TO_FILE}") as file:
            data = file.read()
            my_store.add(data)
        documents = my_store.retrieve("my question").documents
        print(documents)
    """

    client_settings: ClassVar[AstraSettings] = AstraSettings()

    def retrieve(self, text: Optional[Union[str, list[str]]] = None, **kwargs: Any) -> AstraQueryResult:
        """Queries the vectorstore for closest match"""
        embedded_query = self.embedder(text) if text else None
        results = self._collection.vector_find(
            embedded_query,
            limit=kwargs.get('limit', 10),  # Example of additional parameter
            fields=["text", "source"]
        )
        return AstraQueryResult.convert(results)

    def add(self, text: Union[str, list[Document]], **kwargs: Any) -> None:
        """Takes unstructured data and upserts into vectorstore"""
        documents = self.chunker.chunk(text) if isinstance(text, str) else text
        for document in documents:
            self._collection.upsert(document.id, {
                "text": document.text,
                "embeddings": self.embedder(document.text)  # Assuming embeddings are pre-calculated
            })

    ############################# PRIVATE PROPERTIES #################################

   @cached_property
    def _client(self) -> AstraDB:
        """Instantiate and return an AstraDB client configured from settings."""
        try:
            return AstraDB(
                api_endpoint=self.client_settings.api_endpoint,
                token=self.client_settings.application_token,
            )
        except Exception as e:
            logging.error(f"Failed to initialize AstraDB client: {e}")
            raise

    @cached_property
    def _collection(self):
        """Access or create the collection based on the name defined in settings."""
        try:
            return self._client.collection(self.collection_name)
        except Exception as e:
            logging.error(f"Failed to access or create collection: {e}")
