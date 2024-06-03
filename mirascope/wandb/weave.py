"""Integration with Weave from Weights & Biases"""

from typing import Type, overload

import weave

from ..base.ops_utils import get_class_functions
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
def with_weave(
    cls: Type[BaseVectorStoreT],
) -> Type[BaseVectorStoreT]:
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
    for name in get_class_functions(cls):
        setattr(cls, name, weave.op()(getattr(cls, name)))
    if hasattr(cls, "_provider") is False or cls._provider != "openai":
        if hasattr(cls, "configuration"):
            cls.configuration = cls.configuration.model_copy(
                update={"llm_ops": [*cls.configuration.llm_ops, "weave"]}
            )
    return cls
