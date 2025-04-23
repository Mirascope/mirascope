"""The OpenAI-specific implementation of the `LLM` interface."""

from typing import Literal, TypeAlias

from .base import LLM, Client, EmbeddingModel, Params

OPENAI_REGISTERED_LLMS: TypeAlias = Literal["openai:gpt-4o-mini"]


class OpenAIParams(Params, total=False):
    """The parameters for the OpenAI LLM model."""


class OpenAIClient(Client):
    """The client for the OpenAI LLM model."""


class OpenAI(LLM[OpenAIParams, OpenAIClient]):
    """The OpenAI-specific implementation of the `LLM` interface."""


OPENAI_REGISTERED_EMBEDDING_MODELS: TypeAlias = Literal["openai:text-embedding-3-small"]


class OpenAIEmbeddingParams(Params, total=False):
    """The parameters for the OpenAI embedding model."""

    dims: int
    """The number of dimensions for the embedding."""


class OpenAIEmbeddingModel(EmbeddingModel[OpenAIEmbeddingParams, OpenAIClient]):
    """The OpenAI-specific implementation of the `EmbeddingModel` interface."""
