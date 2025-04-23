"""The Google-specific implementation of the `LLM` interface."""

from typing import Literal, TypeAlias

from typing_extensions import NotRequired

from .base import LLM, Client, Params

GOOGLE_REGISTERED_LLMS: TypeAlias = Literal["google:gemini-2.5-flash"]


class GoogleParams(Params):
    """The parameters for the Google LLM model."""

    temperature: NotRequired[float]


class GoogleClient(Client):
    """The client for the Google LLM model."""


class Google(LLM[GoogleParams, GoogleClient]):
    """The Google-specific implementation of the `LLM` interface."""
