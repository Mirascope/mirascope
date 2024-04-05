from typing import Optional

from chromadb import CollectionMetadata

from mirascope.base.types import BaseVectorStoreParams


class ChromaParams(BaseVectorStoreParams):
    metadata: Optional[CollectionMetadata] = None
    get_or_create: bool = False
