"""The Google-specific implementation of the `LLM` interface."""

from typing import Literal, TypeAlias

from .base import LLM, Client, EmbeddingModel, Params

GOOGLE_REGISTERED_LLMS: TypeAlias = Literal["google:gemini-2.5-flash"]


class GoogleParams(Params, total=False):
    """The parameters for the Google LLM model."""

    temperature: float


class GoogleClient(Client):
    """The client for the Google LLM model."""


class Google(LLM[GoogleParams, GoogleClient]):
    """The Google-specific implementation of the `LLM` interface."""


GOOGLE_REGISTERED_EMBEDDING_MODELS: TypeAlias = Literal["gemini-embedding-exp-03-07"]


class GoogleEmbeddingParams(Params, total=False):
    """The parameters for the Google embedding model."""

    dims: int
    """The number of dimensions for the embedding."""


class GoogleEmbeddingModel(EmbeddingModel[GoogleEmbeddingParams, GoogleClient]):
    """The Google-specific implementation of the `EmbeddingModel` interface."""
