"""Tests for the `BaseEmbedder` class."""

from typing import ClassVar
from unittest.mock import patch

from pydantic import BaseModel

from mirascope.rag.embedders import BaseEmbedder
from mirascope.rag.types import BaseEmbeddingParams


@patch.multiple(BaseEmbedder, __abstractmethods__=set())
def test_base_embedder() -> None:
    """Tests the `BaseEmbedder` interface."""
    model = "text-embedding-ada-002"

    class Embedder(BaseEmbedder):
        embedding_params = BaseEmbeddingParams(model=model)

    embedder = Embedder()  # type: ignore
    assert isinstance(embedder, BaseModel)
    assert embedder.embedding_params.model == model


@patch.multiple(BaseEmbedder, __abstractmethods__=set())
def test_extending_base_embedder() -> None:
    """Tests extending the `BaseEmbedder` interface."""

    class EmbeddingParams(BaseEmbeddingParams):
        additional_param: str

    class ExtendedEmbedder(BaseEmbedder):
        embedding_params: ClassVar[EmbeddingParams] = EmbeddingParams(
            model="model", additional_param="param"
        )

    extended_embedder = ExtendedEmbedder()  # type: ignore
    assert extended_embedder.embedding_params.additional_param == "param"

    class MyEmbedder(ExtendedEmbedder):
        embedding_params = EmbeddingParams(model="model", additional_param="my_param")

    my_embedder = MyEmbedder()  # type: ignore
    assert my_embedder.embedding_params.additional_param == "my_param"
