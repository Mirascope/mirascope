"""This module contains the `LiteLLMCallResponseChunk` class.

usage docs: learn/streams.md#handling-streamed-responses
"""

from ..openai import OpenAICallResponseChunk


class LiteLLMCallResponseChunk(OpenAICallResponseChunk):
    """A simpler wrapper around `OpenAICallResponse`.

    Everything is the same except the `cost` property, which has been updated to use
    LiteLLM's cost calculations so that cost tracking works for non-OpenAI models.
    """
