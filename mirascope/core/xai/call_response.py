"""This module contains the `XAICallResponse` class.

usage docs: learn/calls.md#handling-responses
"""

from ..openai import OpenAICallResponse


class XAICallResponse(OpenAICallResponse):
    """A simpler wrapper around `OpenAICallResponse`.

    Everything is the same except the `cost` property, which has been updated to use
    xAI's cost calculations so that cost tracking works for non-OpenAI models.
    """

    _provider = "xai"
