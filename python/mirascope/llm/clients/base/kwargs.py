"""Base Kwargs for client-specific kwarg dicts."""

from typing import TypeVar

# Use TypedDict from typing_extensions for compatibility with google-genai types
from typing_extensions import TypedDict as TypingExtensionsTypedDict

KwargsT = TypeVar("KwargsT", bound="BaseKwargs")


class BaseKwargs(TypingExtensionsTypedDict, total=False):
    """Base class for kwargs by which clients specify options."""
