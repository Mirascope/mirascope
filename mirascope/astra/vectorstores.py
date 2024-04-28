import logging
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
        from mirascope.openai import OpenAIEmbedder
        from mirascope.rag import TextChunker
        from mirascope.astra import AstraSettings, AstraVectorStore
        from typing import ClassVar
        import os
        from astrapy.db import AstraDB

        os.environ["OPENAI_API_KEY"] = "your openai API key here"

        class MyStore(AstraVectorStore):
            collection_name: ClassVar[str] = "your collection name here"
            embedder = OpenAIEmbedder()
            chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
            client_settings = AstraSettings()

        my_store = MyStore()
        with open("test_document.txt") as file:
            data = file.read()
            my_store.add(data)
            documents = my_store.retrieve("Ask a question about the document you uploaded here.").documents
        print(documents)
            """

    client_settings: ClassVar[AstraSettings] = AstraSettings()
    collection_name: ClassVar[str] = "default_collection"  # Default value, can be overridden


    def retrieve(self, text: Optional[Union[str, list[str]]] = None, **kwargs: Any) -> AstraQueryResult:
        """Queries the vectorstore for closest match"""
        embedded_query = self.embedder(text)[0] if text else None
        results = self._collection.vector_find(
            embedded_query,
            limit=kwargs.get('limit', 10),  # Example of additional parameter
            fields=["text", "source"]
        )
        return AstraQueryResult.convert(results)

    def add(self, text: Union[str, list[Document]], **kwargs: Any) -> None:
        """Takes unstructured data and upserts into vectorstore.
        Each document is expected to have text, embeddings, and a source.
        """
        if not text:
            logging.error("No text provided for addition.")
            return
        
        documents = self.chunker.chunk(text) if isinstance(text, str) else text
        for document in documents:
            embeddings = self.embedder(document.text)[0]
            document_to_insert = {
                "text": document.text,
                "$vector": embeddings,  # Include vector embeddings
                "source": kwargs.get("filename", "unknown")  # Optionally include source file name
            }
            self._collection.insert_one(document_to_insert)

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
            raise
