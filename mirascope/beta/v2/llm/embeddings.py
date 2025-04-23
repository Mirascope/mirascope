"""The Embeddings module for embedding text using embedding models."""

import inspect
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Generic, ParamSpec, Protocol, TypeAlias, overload

from typing_extensions import TypeIs, Unpack

from .models import Client, Params

if TYPE_CHECKING:
    from .models.google import (
        GOOGLE_REGISTERED_EMBEDDING_MODELS,
        GoogleClient,
        GoogleEmbeddingParams,
    )
    from .models.openai import (
        OPENAI_REGISTERED_EMBEDDING_MODELS,
        OpenAIClient,
        OpenAIEmbeddingParams,
    )

    REGISTERED_EMBEDDING_MODELS: TypeAlias = (
        GOOGLE_REGISTERED_EMBEDDING_MODELS | OPENAI_REGISTERED_EMBEDDING_MODELS
    )

P = ParamSpec("P")


class Embedding:
    """A class representing an embedding of a text chunk."""

    def __init__(self, text: str, embedding: list[float], model: str) -> None:
        """Initialize an Embedding instance.

        Args:
            text: The text chunk that was embedded
            embedding: The embedding vector
            model: The model used to create the embedding
        """
        self.text = text
        self.embedding = embedding
        self.model = model

    def __repr__(self) -> str:
        """Return a string representation of the embedding."""
        return f"Embedding(text={self.text[:20]}..., model={self.model}, dimensions={len(self.embedding)})"


class EmbeddingFunction(Protocol[P]):
    """Protocol for `embed`-decorated functions."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> list[str]: ...


class AsyncEmbeddingFunction(Protocol[P]):
    """Protocol for asynchronous `embed`-decorated functions."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> list[str]: ...


def embed_fn_is_async(
    fn: EmbeddingFunction | AsyncEmbeddingFunction,
) -> TypeIs[AsyncEmbeddingFunction]:
    return inspect.iscoroutinefunction(fn)


class Embedder(Generic[P]):
    """A class for embedding text using an embedding model."""

    def __init__(self, fn: Callable[P, list[str]]) -> None:
        """Initializes an `Embedder` instance."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> list[Embedding]:
        """Embeds the given text using the embedding model."""
        raise NotImplementedError()


class AsyncEmbedder(Generic[P]):
    """A class for embedding text using an embedding model asynchronously."""

    def __init__(self, fn: Callable[P, Coroutine[None, None, list[str]]]) -> None:
        """Initializes an `AsyncEmbedder` instance."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> list[Embedding]:
        """Embeds the given text using the embedding model asynchronously."""
        raise NotImplementedError()


class EmbedDecorator(Protocol):
    """Protocol for the `embed` decorator."""

    @overload
    def __call__(
        self,
        fn: AsyncEmbeddingFunction[P],
    ) -> AsyncEmbedder[P]: ...

    @overload
    def __call__(
        self,
        fn: EmbeddingFunction[P],
    ) -> Embedder[P]: ...

    def __call__(
        self,
        fn: EmbeddingFunction[P] | AsyncEmbeddingFunction[P],
    ) -> Embedder[P] | AsyncEmbedder[P]: ...


@overload
def embed(
    model: GOOGLE_REGISTERED_EMBEDDING_MODELS,
    *,
    client: GoogleClient | None = None,
    **params: Unpack[GoogleEmbeddingParams],
) -> EmbedDecorator:
    """Overload for Google embedding models."""
    ...


@overload
def embed(
    model: OPENAI_REGISTERED_EMBEDDING_MODELS,
    *,
    client: OpenAIClient | None = None,
    **params: Unpack[OpenAIEmbeddingParams],
) -> EmbedDecorator:
    """Overload for OpenAI embedding models."""
    ...


@overload
def embed(
    model: REGISTERED_EMBEDDING_MODELS,
    *,
    client: Client | None = None,
    **params: Unpack[Params],
) -> EmbedDecorator:
    """Overload for all registered models so that autocomplete works."""
    ...


def embed(
    model: REGISTERED_EMBEDDING_MODELS,
    *,
    client: Client | None = None,
    **params: Unpack[Params],
) -> EmbedDecorator:
    """Decorator for embedding functions.

    Args:
        model: The model identifier to use for embeddings, in the format "provider:model_name"
        dims: The number of dimensions for the embeddings
        custom_client: Optional custom provider client

    Returns:
        A decorator function
    """
    raise NotImplementedError()
