"""The `Metadata` typed dictionary for including general metadata."""

from typing_extensions import NotRequired, TypedDict


class Metadata(TypedDict, total=False):
    """The `Metadata` typed dictionary for including general metadata."""

    tags: NotRequired[set[str]]
