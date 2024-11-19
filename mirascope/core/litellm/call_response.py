"""This module contains the `LiteLLMCallResponse` class.

usage docs: learn/calls.md#handling-responses
"""

from litellm.cost_calculator import completion_cost

from ..openai import OpenAICallResponse


class LiteLLMCallResponse(OpenAICallResponse):
    """A simpler wrapper around `OpenAICallResponse`.

    Everything is the same except the `cost` property, which has been updated to use
    LiteLLM's cost calculations so that cost tracking works for non-OpenAI models.
    """

    _provider = "litellm"

    @property
    def cost(self) -> float | None:
        """Returns the cost of the call."""
        return completion_cost(self.response)
