"""Integration with Weave from Weights & Biases"""

import inspect
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
    ignore_functions = [
        "copy",
        "dict",
        "dump",
        "json",
        "messages",
        "model_copy",
        "model_dump",
        "model_dump_json",
        "model_post_init",
    ]
    for name, _ in inspect.getmembers(cls, predicate=inspect.isfunction):
        if not name.startswith("_") and name not in ignore_functions:
            setattr(cls, name, weave.op()(getattr(cls, name)))
    if hasattr(cls, "_provider") is False or cls._provider != "openai":
        if hasattr(cls, "configuration"):
            cls.configuration = cls.configuration.model_copy(
                update={"llm_ops": [*cls.configuration.llm_ops, "weave"]}
            )
    return cls
