"""The `Metadata` typed dictionary for including general metadata."""

from typing_extensions import NotRequired, TypedDict


class Metadata(TypedDict, total=False):
    """The `Metadata` typed dictionary for including general metadata.

    Attributes:
        tags: A set of strings for tagging calls (e.g. versioning, categorizing, etc.)
    """

    tags: NotRequired[set[str]]
