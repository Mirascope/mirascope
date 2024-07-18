"""Types for interacting with Weaviate using Mirascope."""

from typing import Any, Literal, Optional

import weaviate.types as wt
from pydantic import BaseModel, ConfigDict

from ..base.document import Document
from ..base.vectorstore_params import BaseVectorStoreParams


class WeaviateSettings(BaseModel):
    mode: Literal["local", "cloud", "custom", "embedded"] = "local"
    headers: Optional[dict[str, str]] = None
    cluster_url: Optional[str] = None
    auth_credentials: Optional[Any] = None
    hostname: Optional[str] = None
    port: Optional[int] = None
    grpc_port: Optional[int] = None
    additional_config: Optional[Any] = None
    version: Optional[str] = None
    persistence_data_path: Optional[str] = None
    binary_path: Optional[str] = None
    environment_variables: Optional[dict[str, str]] = None
    http_host: Optional[str] = None
    http_port: Optional[int] = None
    http_secure: Optional[bool] = None
    grpc_host: Optional[str] = None
    grpc_secure: Optional[bool] = None

    skip_init_checks: Optional[bool] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def kwargs(self) -> dict[str, Any]:
        kwargs = {}
        exclude = {"mode"}
        if self.auth_credentials:
            kwargs["auth_credentials"] = self.auth_credentials
            exclude.add("auth_credentials")
        if self.additional_config:
            kwargs["additional_config"] = self.additional_config
            exclude.add("additional_config")
        additional_kwargs = {
            key: value
            for key, value in self.model_dump(exclude=exclude).items()
            if value is not None
        }
        kwargs.update(additional_kwargs)
        return kwargs


class WeaviateParams(BaseVectorStoreParams):
    vectorizer_config: Optional[Any] = None
    generative_config: Optional[Any] = None

    def kwargs(self) -> dict[str, Any]:
        kwargs = {}
        exclude = set()
        if self.vectorizer_config:
            kwargs["vectorizer_config"] = self.vectorizer_config
            exclude = {"vectorizer_config"}
        additional_kwargs = {
            key: value
            for key, value in self.model_dump(exclude=exclude).items()
            if value is not None
        }
        kwargs.update(additional_kwargs)
        return kwargs


class WeaviateQueryResult(BaseModel):
    id: wt.UUID
    documents: Optional[list[Document]]
    metadata: dict[str, Any]
    collection: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def from_response(response_object):
        model_dict = {}
        id = str(response_object.uuid)
        text = response_object.properties["text"]
        model_dict["id"] = id
        doc = Document(id=id, text=text)
        model_dict["documents"] = [doc]
        model_dict["metadata"] = response_object.metadata.__dict__
        model_dict["collection"] = response_object.collection

        return WeaviateQueryResult.model_validate(model_dict)
