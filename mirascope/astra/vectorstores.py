"""A module for calling Astra DB's Client and Collection."""
import logging
from contextlib import suppress
from functools import cached_property
from typing import Any, ClassVar, Optional, Union, Dict
from pydantic import BaseModel

from astrapy.db import AstraDB
from ..rag.types import Document
from ..rag.vectorstores import BaseVectorStore
from .types import AstraParams, AstraQueryResult, AstraSettings

class AstraVectorStoreParams(BaseModel):
    get_or_create: bool = True
    additional_params: Optional[Dict[str, Any]] = {}

class AstraVectorStore(BaseVectorStore):
    """AstraVectorStore integrates AstraDB with a vector storage mechanism, allowing for efficient
    storage and retrieval of document vectors. This class handles the connection and operations
    specific to AstraDB, such as adding and retrieving documents based on vector similarity.

            """

    client_settings: ClassVar[AstraSettings] = AstraSettings()
    index_name: ClassVar[str] = "default_collection"  # Use BaseVectorStore's index_name if applicable
    vectorstore_params: ClassVar[AstraVectorStoreParams] = AstraVectorStoreParams()


    def retrieve(self, text: Optional[Union[str, list[str]]] = None, **kwargs: Any) -> AstraQueryResult:
        """
        Queries the AstraDB vectorstore for documents that are the closest match to the input text.
        
        Args:
            text (str | list[str], optional): The text or list of texts to query against the database.
            **kwargs: Additional keyword arguments for configuring the query, such as limit.

        Returns:
            AstraQueryResult: Contains the documents and possibly embeddings retrieved from the database.
        """

        embedded_query = self.embedder(text)[0] if text else None
        query_params = {**self.vectorstore_params.additional_params, **kwargs}
        results = self._collection.vector_find(
            embedded_query, **query_params
        )

        documents = []
        embeddings = []
        for result in results:
            documents.append([result['text'], result['source']])
            embeddings.append(result['embeddings'])  # Assuming 'embeddings' is part of the results

        return AstraQueryResult(documents=documents, embeddings=embeddings)


    def add(self, text: Union[str, list[Document]], **kwargs: Any) -> None:
        """
        Adds a new document or a list of documents to the AstraDB collection. Each document
        must include the text, its embeddings, and optionally the source.

        Args:
            text (str | list[Document]): The text or documents to be added.
            **kwargs: Additional keyword arguments such as filename which represents the source of the document.
        
        Returns:
            None
        """

        if not text:
            raise ValueError("No text provided for addition.")
        
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
            return AstraDB(**self.client_settings.kwargs())  # Dynamically passing settings
        except Exception as e:
            logging.error(f"Failed to initialize AstraDB client: {e}")
            raise

    @cached_property
    def _collection(self):
        """Access or create the collection based on the parameters."""
        collection_params = {**self.vectorstore_params.dict(), "name": self.index_name}
        return self._client.create_collection(**collection_params)
