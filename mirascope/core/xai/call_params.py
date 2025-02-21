"""usage docs: learn/calls.md#provider-specific-parameters"""

from ..openai import OpenAICallParams


class XAICallParams(OpenAICallParams):
    """A simple wrapper around `OpenAICallParams.`

    Since xAI supports the OpenAI spec, we change nothing here.
    """
