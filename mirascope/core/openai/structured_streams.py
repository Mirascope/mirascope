"""This module contains classes for structured output streaming with OpenAI's API."""

from collections.abc import AsyncGenerator, Generator
from typing import Generic, TypeVar

import jiter
from openai.types.chat import ChatCompletionChunk
from pydantic import BaseModel

from ..base import BaseAsyncStructuredStream, BaseStructuredStream, _partial

_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel)


class OpenAIStructuredStream(
    Generic[_ResponseModelT],
    BaseStructuredStream[ChatCompletionChunk, _ResponseModelT],
):
    """A class for streaming structured outputs from OpenAI's API."""

    def __iter__(self) -> Generator[_ResponseModelT, None, None]:
        """Iterates over the stream and extracts structured outputs."""
        json_output = ""
        for chunk in self.stream:
            if self.json_mode and (content := chunk.choices[0].delta.content):
                json_output += content
            elif (
                (tool_calls := chunk.choices[0].delta.tool_calls)
                and (function := tool_calls[0].function)
                and (arguments := function.arguments)
            ):
                json_output += arguments
            else:
                ValueError("No tool call or JSON object found in response.")
            if json_output:
                json_obj = jiter.from_json(
                    json_output.encode(), partial_mode="trailing-strings"
                )
                yield _partial.partial(self.response_model).model_validate(json_obj)
        yield self.response_model.model_validate_json(json_output)


class OpenAIAsyncStructuredStream(
    Generic[_ResponseModelT],
    BaseAsyncStructuredStream[ChatCompletionChunk, _ResponseModelT],
):
    """A class for async streaming structured outputs from OpenAI's API."""

    def __aiter__(self) -> AsyncGenerator[_ResponseModelT, None]:
        """Iterates over the stream and extracts structured outputs."""

        async def generator():
            nonlocal self
            json_output = ""
            async for chunk in self.stream:
                if self.json_mode and (content := chunk.choices[0].delta.content):
                    json_output += content
                elif (
                    (tool_calls := chunk.choices[0].delta.tool_calls)
                    and (function := tool_calls[0].function)
                    and (arguments := function.arguments)
                ):
                    json_output += arguments
                else:
                    ValueError("No tool call or JSON object found in response.")
                if json_output:
                    json_obj = jiter.from_json(
                        json_output.encode(), partial_mode="trailing-strings"
                    )
                    yield _partial.partial(self.response_model).model_validate(json_obj)
            yield self.response_model.model_validate_json(json_output)

        return generator()
