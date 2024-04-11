"""Tests for the `BaseVectorStore` class."""
from typing import ClassVar
from unittest.mock import patch

from pydantic import BaseModel

from mirascope.rag.types import BaseVectorStoreParams
from mirascope.rag.vectorstores import BaseVectorStore


@patch.multiple(BaseVectorStore, __abstractmethods__=set())
def test_base_vectorstore() -> None:
    """Tests the `BaseVectorStore` interface."""

    class VectorStore(BaseVectorStore):
        vectorstore_params = BaseVectorStoreParams()

    vectorstore = VectorStore()  # type: ignore
    assert isinstance(vectorstore, BaseModel)


@patch.multiple(BaseVectorStore, __abstractmethods__=set())
def test_extending_vectorstore() -> None:
    """Tests extending the `BaseVectorStore` interface."""

    class VectorStoreParams(BaseVectorStoreParams):
        get_or_create: bool

    class ExtendedVectorStore(BaseVectorStore):
        vectorstore_params: ClassVar[VectorStoreParams] = VectorStoreParams(
            get_or_create=True
        )

    extended_vectorstore = ExtendedVectorStore()  # type: ignore
    assert extended_vectorstore.vectorstore_params.get_or_create is True

    class MyVectorStore(ExtendedVectorStore):
        vectorstore_params = VectorStoreParams(get_or_create=True)

    my_vectorstore = MyVectorStore()  # type: ignore
    assert my_vectorstore.vectorstore_params.get_or_create is True
