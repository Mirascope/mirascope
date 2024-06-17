"""Configuration for the Mirascope weaviate module tests."""

import pytest

from mirascope.weaviate.vectorstores import WeaviateVectorStore
from mirascope.weaviate.types import WeaviateSettings, WeaviateParams
import weaviate.classes as wvc
from typing import Optional


@pytest.fixture
def fixture_client() -> WeaviateVectorStore:
    """Fixture for a local WeaviateVectorStore"""

    class VectorStore(WeaviateVectorStore):
        index_name = "test"
        client_settings = WeaviateSettings()

    return VectorStore()


@pytest.fixture
def fixture_client_with_vectorizer() -> WeaviateVectorStore:
    """Fixture for a local WeaviateVectorStore that uses a vectorizer"""

    class VectorStoreWithVectorizer(WeaviateVectorStore):
        index_name = "index_with_vectorizer"
        client_settings = WeaviateSettings(headers={"X-OpenAI-Api-Key": "dummy_key"})
        vectorstore_params = WeaviateParams(
            vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai()
        )

    return VectorStoreWithVectorizer()


@pytest.fixture
def fixture_embedded_client() -> WeaviateVectorStore:
    """Fixture for an embedded WeaviateVectorStore"""

    class VectorStore(WeaviateVectorStore):
        index_name = "test"
        client_settings = WeaviateSettings(mode="embedded")

    return VectorStore()


@pytest.fixture
def fixture_weaviate_cloud_client() -> WeaviateVectorStore:
    """Fixture for a cloud-hosted WeaviateVectorStore"""

    class VectorStore(WeaviateVectorStore):
        index_name = "test"
        client_settings = WeaviateSettings(
            cluster_url="url", auth_credentials="auth_credentials", mode="cloud"
        )

    return VectorStore()


@pytest.fixture
def fixture_weaviate_custom_client() -> WeaviateVectorStore:
    """Fixture for a custom-hosted WeaviateVectorStore"""

    class VectorStore(WeaviateVectorStore):
        index_name = "test"
        client_settings = WeaviateSettings(
            http_host="http_host",
            http_port=443,
            http_secure=True,
            grpc_host="grpc_host",
            grpc_port=443,
            grpc_secure=True,
            additional_config="additional_config",
            auth_credentials="auth_credentials",
            mode="custom",
        )

    return VectorStore()


class Metadata:
    foo: str = "bar"


class NearText:
    uuid: str = "foo"
    properties: dict[str, str] = {"text": "dummy text"}
    metadata: Metadata = Metadata()
    collection: Optional[str] = None


@pytest.fixture
def fixture_weaviate_raw_near_text_query() -> NearText:
    """Fixture for a weaviate Near_text query return object"""
    return NearText()
