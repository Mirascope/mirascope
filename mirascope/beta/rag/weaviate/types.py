"""Types for interacting with Weaviate using Mirascope."""

from __future__ import annotations

from typing import Any, Literal

import weaviate.types as wt
from pydantic import BaseModel, ConfigDict

from ..base.document import Document
from ..base.vectorstore_params import BaseVectorStoreParams


class WeaviateSettings(BaseModel):
    mode: Literal["local", "cloud", "custom", "embedded"] = "local"
    headers: dict[str, str] | None = None
    cluster_url: str | None = None
    auth_credentials: Any | None = None
    hostname: str | None = None
    port: int | None = None
    grpc_port: int | None = None
    additional_config: Any | None = None
    version: str | None = None
    persistence_data_path: str | None = None
    binary_path: str | None = None
    environment_variables: dict[str, str] | None = None
    http_host: str | None = None
    http_port: int | None = None
    http_secure: bool | None = None
    grpc_host: str | None = None
    grpc_secure: bool | None = None

    skip_init_checks: bool | None = None

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
    vectorizer_config: Any | None = None
    generative_config: Any | None = None

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
    documents: list[Document] | None
    metadata: dict[str, Any]
    collection: str | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def from_response(response_object) -> WeaviateQueryResult:
        model_dict = {}
        id = str(response_object.uuid)
        text = response_object.properties["text"]
        model_dict["id"] = id
        doc = Document(id=id, text=text)
        model_dict["documents"] = [doc]
        model_dict["metadata"] = response_object.metadata.__dict__
        model_dict["collection"] = response_object.collection

        return WeaviateQueryResult.model_validate(model_dict)
