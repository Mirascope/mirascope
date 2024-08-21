"""Utility for getting the possible most recent user message."""

from typing import TypeVar

_T = TypeVar("_T")


def get_possible_user_message_param(messages: list[_T]) -> _T | None:
    """Get the possible most recent user message."""
    if not messages:
        return None
    most_recent_message = messages[-1]
    if (
        isinstance(most_recent_message, dict)
        and "role" in most_recent_message
        and most_recent_message["role"] == "user"
    ):
        return most_recent_message
    if hasattr(most_recent_message, "role") and most_recent_message.role == "user":  # pyright: ignore [reportAttributeAccessIssue]
        return most_recent_message
    return None
