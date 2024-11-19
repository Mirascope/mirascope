"""usage docs: learn/calls.md#provider-specific-parameters"""

from ..openai import OpenAICallParams


class LiteLLMCallParams(OpenAICallParams):
    """A simple wrapper around `OpenAICallParams.`

    Since LiteLLM uses the OpenAI spec, we change nothing here.
    """
