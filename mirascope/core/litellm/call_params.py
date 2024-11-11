"""usage docs: learn/calls.md#provider-specific-parameters"""

from typing_extensions import Unpack

from ..base.call_params import CommonCallParams
from ..openai import OpenAICallParams
from ..openai.call_params import get_openai_call_params_from_common


class LiteLLMCallParams(OpenAICallParams):
    """A simple wrapper around `OpenAICallParams.`

    Since LiteLLM uses the OpenAI spec, we change nothing here.
    """


def get_litellm_call_params_from_common(
    **params: Unpack[CommonCallParams],
) -> OpenAICallParams:
    """Converts common call parameters to LiteLLM-specific call parameters.

    Note: LiteLLM follows the OpenAI API spec, so we use OpenAICallParams.
    """
    return get_openai_call_params_from_common(**params)
