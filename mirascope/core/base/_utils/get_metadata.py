"""Utility for pulling metadata from a call and merging with any dynamic metadata."""

from typing import Callable

from ..dynamic_config import BaseDynamicConfig
from ..metadata import Metadata


def get_metadata(fn: Callable, dynamic_config: BaseDynamicConfig) -> Metadata:
    """Get the metadata from the function and merge with any dynamic metadata."""
    metadata = fn.__annotations__.get("metadata", {})
    if dynamic_metadata := getattr(dynamic_config, "metadata", {}):
        metadata = metadata | dynamic_metadata
    return metadata
