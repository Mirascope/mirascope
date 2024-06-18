"""Tests for Mirascope WeaviateVectorStore class"""

from unittest.mock import ANY, MagicMock, patch, PropertyMock

from mirascope.weaviate.vectorstores import WeaviateVectorStore
from mirascope.rag import Document
import weaviate.classes as wvc
from tests.weaviate.conftest import NearText


@patch("weaviate.connect_to_local", new_callable=MagicMock)
def test_weaviate_vectorstore_local_mode(
    mock_connect_to_local: MagicMock, fixture_client: WeaviateVectorStore
):
    """Test the _client property with mode=local of the WeaviateVectorStore class."""
    fixture_client._client
    mock_connect_to_local.assert_called_once_with()


@patch("weaviate.connect_to_embedded", new_callable=MagicMock)
def test_weaviate_vectorstore_embedded_mode(
    mock_connect_to_embedded: MagicMock, fixture_embedded_client: WeaviateVectorStore
):
    """Test the _client property with mode=embedded of the WeaviateVectorStore class."""
    fixture_embedded_client._client
    mock_connect_to_embedded.assert_called_once_with()


@patch("weaviate.connect_to_weaviate_cloud", new_callable=MagicMock)
def test_weaviate_vectorstore_cloud_mode(
    mock_connect_to_cloud: MagicMock, fixture_weaviate_cloud_client: WeaviateVectorStore
):
    """Test the _client property with the mode=cloud of the WeaviateVectorStore class"""
    fixture_weaviate_cloud_client._client
    cluster_url = "url"
    auth_credentials = "auth_credentials"

    mock_connect_to_cloud.assert_called_once_with(
        cluster_url=cluster_url, auth_credentials=auth_credentials
    )


@patch("weaviate.connect_to_custom", new_callable=MagicMock)
def test_weaviate_vectorstore_custom_mode_with_configs(
    mock_connect_to_custom: MagicMock,
    fixture_weaviate_custom_client: WeaviateVectorStore,
):
    """Test the _client property with the mode=cloud of the WeaviateVectorStore class"""
    fixture_weaviate_custom_client._client
    http_host = "http_host"
    http_port = 443
    http_secure = True
    grpc_host = "grpc_host"
    grpc_port = 443
    grpc_secure = True
    additional_config = "additional_config"
    auth_credentials = "auth_credentials"

    mock_connect_to_custom.assert_called_once_with(
        http_host=http_host,
        http_port=http_port,
        http_secure=http_secure,
        grpc_host=grpc_host,
        grpc_port=grpc_port,
        grpc_secure=grpc_secure,
        additional_config=additional_config,
        auth_credentials=auth_credentials,
    )


mock_client = MagicMock(spec=["close"])


@patch.object(WeaviateVectorStore, "_client", new_callable=PropertyMock)
def test_weaviate_vectorstore_index_with_vectorizer(
    mock_client: MagicMock, fixture_client_with_vectorizer: WeaviateVectorStore
):
    """Test the insertion of a vectorizer into the kwargs of the WeaviateParams when called with WeaviateVectorStore._index"""
    mock_client.return_value.collections.create = MagicMock()
    index_name = "index_with_vectorizer"
    vectorizer = wvc.config.Configure.Vectorizer.text2vec_openai()
    mock_client.return_value.collections.exists.return_value = False

    fixture_client_with_vectorizer.add("dummy_text")

    mock_client.return_value.collections.create.assert_called_once_with(
        vectorizer_config=vectorizer, name=index_name
    )


@patch.object(WeaviateVectorStore, "_client", new_callable=PropertyMock)
def test_weaviate_vectorstore_index_get_existing_collection(
    mock_client: MagicMock, fixture_client: WeaviateVectorStore
):
    mock_client.return_value.collections.exists.return_value = True
    mock_client.return_value.collections.get = MagicMock()
    fixture_client.add("dummy text")

    mock_client.return_value.collections.get.assert_called_once_with("test")


@patch.object(WeaviateVectorStore, "_client", new_callable=PropertyMock)
def test_weaviate_vectorstore_close_connection(
    mock_client: PropertyMock, fixture_client: WeaviateVectorStore
):
    """Test that the close_connection method properly calls the client's close method."""
    mock_client.return_value.close = MagicMock()

    fixture_client.close_connection()

    mock_client.return_value.close.assert_called_once_with()


@patch.object(WeaviateVectorStore, "_client", new_callable=PropertyMock)
@patch("weaviate.collections.data._DataCollection.insert", new_callable=MagicMock)
def test_weaviate_vectorstore_add_single_text(
    mock_weaviate_insert: MagicMock,
    mock_client: PropertyMock,
    fixture_client: WeaviateVectorStore,
):
    """Test the add method of the WeaviateVectorStore class with a single string as an argument"""
    mock_index = MagicMock()
    mock_client.return_value.collections.exists.return_value = False
    mock_client.return_value.collections.create.return_value = mock_index
    mock_index.data.insert = mock_weaviate_insert

    fixture_client.add("dummy text")

    mock_weaviate_insert.assert_called_once_with(
        properties={"text": "dummy text"}, uuid=ANY
    )


@patch.object(WeaviateVectorStore, "_client", new_callable=PropertyMock)
@patch("weaviate.collections.data._DataCollection.insert_many", new_callable=MagicMock)
def test_weaviate_vectorstore_add_document_list(
    mock_weaviate_insert_many: MagicMock,
    mock_client: PropertyMock,
    fixture_client: WeaviateVectorStore,
):
    """Test the add method of the WeaviateVectorStore class with a document"""
    mock_index = MagicMock()
    mock_client.return_value.collections.exists.return_value = False

    mock_client.return_value.collections.create.return_value = mock_index
    mock_index.data.insert_many = mock_weaviate_insert_many

    docs = [Document(text="foo", id="1"), Document(text="bar", id="2")]
    fixture_client.add(docs)

    mock_weaviate_insert_many.assert_called_once()


@patch.object(WeaviateVectorStore, "_client", new_callable=PropertyMock)
@patch("weaviate.collections.queries.near_text", new_callable=MagicMock)
def test_weaviate_vectorstore_retrieve(
    mock_weaviate_retrieve: MagicMock,
    mock_client: MagicMock,
    fixture_client: WeaviateVectorStore,
    fixture_weaviate_raw_near_text_query: NearText,
):
    """Test the retrieve method of the WeaviateVectorStore class with a document"""
    mock_index = MagicMock()
    mock_client.return_value.collections.exists.return_value = False
    mock_client.return_value.collections.create.return_value = mock_index
    mock_index.query.near_text = mock_weaviate_retrieve

    mock_weaviate_retrieve.return_value.objects = [fixture_weaviate_raw_near_text_query]

    fixture_client.retrieve("dummy text")

    mock_weaviate_retrieve.assert_called_once_with(query="dummy text")
