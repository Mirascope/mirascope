"""Types for interacting with Pinecone using Mirascope."""
from typing import Any, Literal, Optional

from pinecone.config import Config
from pinecone.core.client.api.manage_indexes_api import ManageIndexesApi
from pydantic import BaseModel, ConfigDict

from ..rag.types import BaseVectorStoreParams


class ServerlessSpec(BaseModel):
    cloud: str
    region: str

    def kwargs(self) -> dict[str, Any]:
        """Returns all parameters for the index as a keyword arguments dictionary."""
        kwargs = {
            key: value for key, value in self.model_dump().items() if value is not None
        }
        return {"serverless": kwargs}


class PodSpec(BaseModel):
    environment: str
    replicas: Optional[int] = None
    shards: Optional[int] = None
    pods: Optional[int] = None
    pod_type: Optional[str] = "p1.x1"
    metadata_config: Optional[dict] = {}
    source_collection: Optional[str] = None

    def kwargs(self) -> dict[str, Any]:
        """Returns all parameters for the index as a keyword arguments dictionary."""
        kwargs = {
            key: value for key, value in self.model_dump().items() if value is not None
        }
        return {"pod": kwargs}


class PineconeParams(BaseModel):
    metric: Optional[Literal["cosine", "dotproduct", "euclidean"]] = "cosine"
    timeout: Optional[int] = None

    def kwargs(self) -> dict[str, Any]:
        """Returns all parameters for the index as a keyword arguments dictionary."""
        kwargs = {
            key: value for key, value in self.model_dump().items() if value is not None
        }
        return kwargs


class PineconeServerlessParams(PineconeParams, ServerlessSpec, BaseVectorStoreParams):
    def kwargs(self) -> dict[str, Any]:
        """Returns all parameters for the index as a keyword arguments dictionary."""
        serverless_kwargs = ServerlessSpec(**self.model_dump()).kwargs()
        pinecone_kwargs = PineconeParams(**self.model_dump()).kwargs()
        return {**pinecone_kwargs, "spec": {**serverless_kwargs}}


class PineconePodParams(PineconeParams, PodSpec, BaseVectorStoreParams):
    def kwargs(self) -> dict[str, Any]:
        """Returns all parameters for the index as a keyword arguments dictionary."""
        pod_kwargs = PodSpec(**self.model_dump()).kwargs()
        pinecone_kwargs = PineconeParams(**self.model_dump()).kwargs()
        # print(pinecone_kwargs, serverless_kwargs)
        return {**pinecone_kwargs, "spec": {**pod_kwargs}}


class PineconeSettings(BaseModel):
    api_key: Optional[str] = None
    host: Optional[str] = None
    proxy_url: Optional[str] = None
    proxy_headers: Optional[dict[str, str]] = None
    ssl_ca_certs: Optional[str] = None
    ssl_verify: Optional[bool] = None
    config: Optional[Config] = None
    additional_headers: Optional[dict[str, str]] = {}
    pool_threads: Optional[int] = 1
    index_api: Optional[ManageIndexesApi] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def kwargs(self) -> dict[str, Any]:
        """Returns all parameters for the index as a keyword arguments dictionary."""
        kwargs = {
            key: value for key, value in self.model_dump().items() if value is not None
        }
        return kwargs


class PineconeQueryResult(BaseModel):
    ids: list[str]
    documents: Optional[list[str]] = None
    scores: Optional[list[float]] = None
    embeddings: Optional[list[list[float]]] = None
