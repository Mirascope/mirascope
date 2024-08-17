"""The Mirascope LiteLLM Module."""

from ._call import litellm_call
from ._call import litellm_call as call

__all__ = ["call", "litellm_call"]
