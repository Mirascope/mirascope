"""Utility for pulling metadata from a call and merging with any dynamic metadata."""

from collections.abc import Callable

from pydantic import BaseModel

from ..dynamic_config import BaseDynamicConfig
from ..metadata import Metadata


def get_metadata(
    fn: Callable | BaseModel, dynamic_config: BaseDynamicConfig
) -> Metadata:
    """Get the metadata from the function and merge with any dynamic metadata."""
    if dynamic_config and "metadata" in dynamic_config:
        return dynamic_config["metadata"]
    return getattr(fn, "_metadata", Metadata())
