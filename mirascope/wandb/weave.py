"""Integration with Weave from Weights & Biases"""

from typing import Type, overload

import weave

from ..types import (
    BaseCallT,
    BaseChunkerT,
    BaseEmbedderT,
    BaseExtractorT,
    BaseVectorStoreT,
)


@overload
def with_weave(cls: Type[BaseCallT]) -> Type[BaseCallT]:
    ...  # pragma: no cover


@overload
def with_weave(
    cls: Type[BaseExtractorT],
) -> Type[BaseExtractorT]:
    ...  # pragma: no cover


@overload
def with_weave(cls: Type[BaseVectorStoreT]) -> Type[BaseVectorStoreT]:
    ...  # pragma: no cover


@overload
def with_weave(cls: Type[BaseChunkerT]) -> Type[BaseChunkerT]:
    ...  # pragma: no cover


@overload
def with_weave(cls: Type[BaseEmbedderT]) -> Type[BaseEmbedderT]:
    ...  # pragma: no cover


def with_weave(cls):
    """Wraps base classes to automatically use weave.

    Supported base classes: `BaseCall`, `BaseExtractor`, `BaseVectorStore`,
    `BaseChunker`, `BaseEmbedder`

    Example:

    ```python
    import weave

    from mirascope.openai import OpenAICall
    from mirascope.wandb import with_weave

    weave.init("my-project")


    @with_weave
    class BookRecommender(OpenAICall):
        prompt_template = "Please recommend some {genre} books"

        genre: str


    recommender = BookRecommender(genre="fantasy")
    response = recommender.call()  # this will automatically get logged with weave
    print(response.content)
    ```
    """
    if hasattr(cls, "call"):
        setattr(cls, "call", weave.op()(cls.call))
    if hasattr(cls, "call_async"):
        setattr(cls, "call_async", weave.op()(cls.call_async))

    # VectorStore
    if hasattr(cls, "retrieve"):
        setattr(cls, "retrieve", weave.op()(cls.retrieve))
    if hasattr(cls, "add"):
        setattr(cls, "add", weave.op()(cls.add))

    # Chunker
    if hasattr(cls, "chunk"):
        setattr(cls, "chunk", weave.op()(cls.chunk))

    # Embedder
    if hasattr(cls, "embed"):
        setattr(cls, "embed", weave.op()(cls.embed))
    if hasattr(cls, "embed_async"):
        setattr(cls, "embed_async", weave.op()(cls.embed_async))

    # It appears Weave does not yet support streaming or does it in a different way? :(
    # Our calls will be tracked, but the sub-calls don't since the streaming happens
    # when iterating through the generator after the call.
    if hasattr(cls, "stream"):
        setattr(cls, "stream", weave.op()(cls.stream))
    if hasattr(cls, "stream_async"):
        setattr(cls, "stream_async", weave.op()(cls.stream_async))

    if hasattr(cls, "extract"):
        setattr(cls, "extract", weave.op()(cls.extract))
    if hasattr(cls, "extract_async"):
        setattr(cls, "extract_async", weave.op()(cls.extract_async))

    if hasattr(cls, "call_params"):
        setattr(
            cls, "call_params", cls.call_params.model_copy(update={"weave": weave.op()})
        )
    if hasattr(cls, "vectorstore_params"):
        setattr(
            cls,
            "vectorstore_params",
            cls.vectorstore_params.model_copy(update={"weave": weave.op()}),
        )
    return cls
