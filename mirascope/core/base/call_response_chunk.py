"""This module contains the `BaseCallResponseChunk` class.

usage docs: learn/streams.md#handling-streamed-responses
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

from mirascope.core.base._utils import get_common_usage
from mirascope.core.base.types import CostMetadata, FinishReason, Usage

_ChunkT = TypeVar("_ChunkT", bound=Any)
_FinishReasonT = TypeVar("_FinishReasonT", bound=Any)


class BaseCallResponseChunk(BaseModel, Generic[_ChunkT, _FinishReasonT], ABC):
    """A base abstract interface for LLM streaming response chunks.

    Attributes:
        chunk: The original response chunk from whichever model response this wraps.
    """

    chunk: _ChunkT

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    def __str__(self) -> str:
        """Returns the string content of the chunk."""
        return self.content

    @property
    @abstractmethod
    def content(self) -> str:
        """Should return the string content of the response chunk.

        If there are multiple choices in a chunk, this method should select the 0th
        choice and return it's string content.

        If there is no string content (e.g. when using tools), this method must return
        the empty string.
        """
        ...

    @property
    @abstractmethod
    def finish_reasons(self) -> list[_FinishReasonT] | None:
        """Should return the finish reasons of the response.

        If there is no finish reason, this method must return None.
        """
        ...

    @property
    @abstractmethod
    def model(self) -> str | None:
        """Should return the name of the response model."""
        ...

    @property
    @abstractmethod
    def id(self) -> str | None:
        """Should return the id of the response."""
        ...

    @property
    @abstractmethod
    def usage(self) -> Any:  # noqa: ANN401
        """Should return the usage of the response.

        If there is no usage, this method must return None.
        """
        ...

    @property
    @abstractmethod
    def input_tokens(self) -> int | float | None:
        """Should return the number of input tokens.

        If there is no input_tokens, this method must return None.
        """
        ...

    @property
    @abstractmethod
    def cached_tokens(self) -> int | float | None:
        """Should return the number of cached tokens.

        If there is no cached_tokens, this method must return None.
        """
        ...

    @property
    @abstractmethod
    def output_tokens(self) -> int | float | None:
        """Should return the number of output tokens.

        If there is no output_tokens, this method must return None.
        """
        ...

    @property
    @abstractmethod
    def cost_metadata(self) -> CostMetadata:
        """Get metadata required for cost calculation.

        Returns:
            A CostMetadata object with information relevant to cost calculation
        """
        return CostMetadata(
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            cached_tokens=self.cached_tokens,
        )

    @property
    @abstractmethod
    def common_finish_reasons(self) -> list[FinishReason] | None:
        """Provider-agnostic finish reasons."""
        ...

    @property
    def common_usage(self) -> Usage | None:
        """Provider-agnostic usage info."""
        return get_common_usage(
            self.input_tokens, self.cached_tokens, self.output_tokens
        )
