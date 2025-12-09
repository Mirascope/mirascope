from __future__ import annotations

import abc
from collections.abc import Iterable, Sequence
from typing import TypeAlias

from mlx_lm.generate import GenerationResponse

from ....formatting import Format, FormattableT
from ....messages import AssistantContent, Message
from ....responses import ChunkIterator
from ....tools import AnyToolSchema, BaseToolkit

TokenIds: TypeAlias = list[int]


class BaseEncoder(abc.ABC):
    """Abstract base class for Mirascope <> MLX encoding and decoding."""

    @abc.abstractmethod
    def encode_request(
        self,
        messages: Sequence[Message],
        tools: Sequence[AnyToolSchema] | BaseToolkit[AnyToolSchema] | None,
        format: type[FormattableT] | Format[FormattableT] | None,
    ) -> tuple[Sequence[Message], Format[FormattableT] | None, TokenIds]:
        """Encode the request messages into a format suitable for the model.

        Args:
            messages: The sequence of messages to encode.
            tools: Optional sequence of tool schemas or toolkit for the model.
            format: Optional format specification for structured outputs.

        Returns:
            A tuple containing:
                - The processed messages
                - The format specification (if provided)
                - The encoded prompt as token IDs
        """

        ...

    @abc.abstractmethod
    def decode_response(
        self, stream: Iterable[GenerationResponse]
    ) -> tuple[AssistantContent, GenerationResponse | None]:
        """Decode a stream of MLX generation responses into assistant content.

        Args:
            stream: An iterable of MLX generation responses.

        Returns:
            A tuple containing:
                - The decoded assistant content
                - The final generation response (if available)
        """
        ...

    @abc.abstractmethod
    def decode_stream(self, stream: Iterable[GenerationResponse]) -> ChunkIterator:
        """Decode a stream of MLX generation responses into an iterable of chunks.

        Args:
            stream: An iterable of MLX generation responses.

        Returns:
            A ChunkIterator yielding content chunks for streaming responses.
        """
        ...
