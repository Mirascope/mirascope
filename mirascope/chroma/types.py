from typing import Optional

from chromadb import CollectionMetadata
from chromadb.api.types import URI, Document, IDs, Loadable, Metadata
from chromadb.types import Vector
from pydantic import BaseModel, ConfigDict

from mirascope.base.types import BaseVectorStoreParams


class ChromaParams(BaseVectorStoreParams):
    metadata: Optional[CollectionMetadata] = None
    get_or_create: bool = False


class ChromaQueryResult(BaseModel):
    ids: list[IDs]
    embeddings: Optional[list[list[Vector]]]
    documents: Optional[list[list[Document]]]
    uris: Optional[list[list[URI]]]
    data: Optional[list[Loadable]]
    metadatas: Optional[list[list[Optional[Metadata]]]]
    distances: Optional[list[list[float]]]

    model_config = ConfigDict(arbitrary_types_allowed=True)
