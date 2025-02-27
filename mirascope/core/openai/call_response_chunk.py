"""This module contains the `OpenAICallResponseChunk` class.

usage docs: learn/streams.md#handling-streamed-responses
"""

from __future__ import annotations

import base64
from typing import cast

from openai.types.chat import ChatCompletionChunk
from openai.types.chat.chat_completion_chunk import Choice
from openai.types.completion_usage import CompletionUsage
from pydantic import SkipValidation, computed_field

from ..base import BaseCallResponseChunk
from ..base.types import CostMetadata

FinishReason = Choice.__annotations__["finish_reason"]


class OpenAICallResponseChunk(BaseCallResponseChunk[ChatCompletionChunk, FinishReason]):
    """A convenience wrapper around the OpenAI `ChatCompletionChunk` streamed chunks.

    When calling the OpenAI API using a function decorated with `openai_call` and
    `stream` set to `True`, the stream will contain `OpenAIResponseChunk` instances with
    properties that allow for more convenient access to commonly used attributes.

    Example:

    ```python
    from mirascope.core import prompt_template
    from mirascope.core.openai import openai_call


    @openai_call("gpt-4o-mini", stream=True)
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    stream = recommend_book("fantasy")  # response is an `OpenAIStream`
    for chunk, _ in stream:
        print(chunk.content, end="", flush=True)
    ```
    """

    chunk: SkipValidation[ChatCompletionChunk]

    @property
    def content(self) -> str:
        """Returns the content for the 0th choice delta."""
        delta = None
        if self.chunk.choices:
            delta = self.chunk.choices[0].delta
        return delta.content if delta is not None and delta.content else ""

    @property
    def finish_reasons(self) -> list[FinishReason]:
        """Returns the finish reasons of the response."""
        return [
            choice.finish_reason
            for choice in self.chunk.choices
            if choice.finish_reason
        ]

    @property
    def model(self) -> str:
        """Returns the name of the response model."""
        return self.chunk.model

    @property
    def id(self) -> str:
        """Returns the id of the response."""
        return self.chunk.id

    @property
    def usage(self) -> CompletionUsage | None:
        """Returns the usage of the chat completion."""
        if hasattr(self.chunk, "usage") and self.chunk.usage:
            return self.chunk.usage
        return None

    @computed_field
    @property
    def cached_tokens(self) -> int | None:
        """Returns the number of cached tokens."""
        return (
            details.cached_tokens
            if hasattr(self.chunk, "usage")
            and self.usage
            and (details := getattr(self.usage, "prompt_tokens_details", None))
            else None
        )

    @property
    def input_tokens(self) -> int | None:
        """Returns the number of input tokens."""
        if self.usage:
            return self.usage.prompt_tokens
        return None

    @property
    def output_tokens(self) -> int | None:
        """Returns the number of output tokens."""
        if self.usage:
            return self.usage.completion_tokens
        return None

    @computed_field
    @property
    def audio(self) -> bytes | None:
        """Returns the audio data of the response."""

        if self.chunk.choices and (
            (audio := getattr(self.chunk.choices[0].delta, "audio", None))
            and (audio_data := audio.get("data"))
        ):
            return base64.b64decode(audio_data)
        return None

    @computed_field
    @property
    def audio_transcript(self) -> str | None:
        """Returns the transcript of the audio content."""
        if self.chunk.choices and (
            audio := getattr(self.chunk.choices[0].delta, "audio", None)
        ):
            return audio.get("transcript")
        return None

    @property
    def cost_metadata(self) -> CostMetadata:
        """Returns the cost metadata."""
        return super().cost_metadata

    @property
    def common_finish_reasons(self) -> list[FinishReason] | None:
        """Provider-agnostic finish reasons."""
        return cast(list[FinishReason], self.finish_reasons)
