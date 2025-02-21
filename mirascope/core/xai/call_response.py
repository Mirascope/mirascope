"""This module contains the `XAICallResponse` class.

usage docs: learn/calls.md#handling-responses
"""

from pydantic import computed_field

from ..openai import OpenAICallResponse
from ._utils import calculate_cost


class XAICallResponse(OpenAICallResponse):
    """A simpler wrapper around `OpenAICallResponse`.

    Everything is the same except the `cost` property, which has been updated to use
    xAI's cost calculations so that cost tracking works for non-OpenAI models.
    """

    _provider = "xai"

    @computed_field
    @property
    def cost(self) -> float | None:
        """Returns the cost of the call."""
        return calculate_cost(
            self.input_tokens, self.cached_tokens, self.output_tokens, self.model
        )
