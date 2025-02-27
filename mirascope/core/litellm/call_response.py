"""This module contains the `LiteLLMCallResponse` class.

usage docs: learn/calls.md#handling-responses
"""

from pydantic import computed_field

from ..base.types import CostMetadata
from ..openai import OpenAICallResponse


class LiteLLMCallResponse(OpenAICallResponse):
    """A simpler wrapper around `OpenAICallResponse`.

    Everything is the same except the `cost` property, which has been updated to use
    LiteLLM's cost calculations so that cost tracking works for non-OpenAI models.
    """

    _provider = "litellm"

    @computed_field
    @property
    def cost_metadata(self) -> CostMetadata:
        return CostMetadata(cost=self.response._hidden_params["response_cost"])  # pyright: ignore [reportAttributeAccessIssue]
