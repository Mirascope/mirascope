"""This module contains the base class for message parameters."""

from typing import Literal

from typing_extensions import TypedDict


class BaseMessageParam(TypedDict):
    """A base class for message parameters.

    Available roles: `system`, `user`, `assistant`, `model`.
    """

    role: Literal["system", "user", "assistant", "model"]
    content: str
