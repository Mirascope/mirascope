"""The Google-specific implementation of the `LLM` interface."""

from google.genai.types import ContentDict, FunctionResponse

from ..messages import Message
from .base import LLM, Client, Params


class GoogleParams(Params, total=False):
    """The parameters for the Google LLM model."""

    temperature: float


class GoogleClient(Client):
    """The client for the Google LLM model."""


class Google(LLM[Message | ContentDict | FunctionResponse, GoogleParams, GoogleClient]):
    """The Google-specific implementation of the `LLM` interface."""
