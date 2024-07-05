"""Utility for pulling the tags from a call and merging with any dynamic tags."""

from typing import Callable

from ..dynamic_config import BaseDynamicConfig


def get_tags(fn: Callable, dynamic_config: BaseDynamicConfig) -> set[str]:
    """Get the tags from the function and merge with any dynamic tags."""
    tags: set[str] = fn.__annotations__.get("tags", set())
    if dynamic_tags := getattr(dynamic_config, "tags", set()):
        tags = tags | dynamic_tags
    return set(tags)
