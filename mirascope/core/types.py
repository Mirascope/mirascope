"""Mirascope Core Types."""

from typing import Literal

from typing_extensions import TypedDict


class MessageParam(TypedDict):
    """A base class for message parameters.

    Available roles: `system`, `user`, `assistant`, `model`.
    """

    role: Literal["system", "user", "assistant", "model"]
    content: str
