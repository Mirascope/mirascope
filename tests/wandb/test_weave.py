"""Tests for the Mirascope + Weave integration."""
from typing import Type

import weave

from mirascope.chroma.vectorstores import ChromaVectorStore
from mirascope.openai import OpenAICall, OpenAIEmbedder, OpenAIExtractor
from mirascope.rag.chunkers import BaseChunker, TextChunker
from mirascope.rag.types import Document
from mirascope.wandb.weave import with_weave


@with_weave
class MyCall(OpenAICall):
    prompt_template = "test"


def test_call_with_weave() -> None:
    my_call = MyCall()
    assert isinstance(my_call.call, weave.Op)
    assert isinstance(my_call.call_async, weave.Op)
    assert isinstance(my_call.stream, weave.Op)
    assert isinstance(my_call.stream_async, weave.Op)
    assert my_call.call_params.weave is not None


@with_weave
class MyExtractor(OpenAIExtractor[int]):
    extract_schema: Type[int] = int
    prompt_template = "test"


def test_extractor_with_weave() -> None:
    my_extractor = MyExtractor()
    assert isinstance(my_extractor.extract, weave.Op)
    assert isinstance(my_extractor.extract_async, weave.Op)
    assert my_extractor.call_params.weave is not None


@with_weave
class MyStore(ChromaVectorStore):
    embedder = OpenAIEmbedder()
    chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
    index_name = "test-0001"


def test_vectorstore_with_weave() -> None:
    my_store = MyStore()
    assert isinstance(my_store.retrieve, weave.Op)
    assert isinstance(my_store.add, weave.Op)
    assert my_store.vectorstore_params.weave is not None


@with_weave
class MyEmbedder(OpenAIEmbedder):
    ...


def test_embedder_with_weave() -> None:
    my_embedder = MyEmbedder()
    assert isinstance(my_embedder.embed, weave.Op)
    assert isinstance(my_embedder.embed_async, weave.Op)


@with_weave
class MyChunker(BaseChunker):
    def chunk(self, text: str) -> list[Document]:
        return [Document(text=text, id="1")]


def test_chunker_with_weave() -> None:
    my_chunker = MyChunker()
    my_chunker.chunk("test")
    assert isinstance(my_chunker.chunk, weave.Op)
