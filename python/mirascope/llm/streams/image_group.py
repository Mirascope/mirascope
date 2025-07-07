"""Image group classes for streaming image content."""

from typing import Literal

from ..content import Image, ImageChunk
from .groups import BaseAsyncGroup, BaseGroup


class ImageGroup(BaseGroup[ImageChunk, Image]):
    """Group for streaming image content chunks."""

    @property
    def type(self) -> Literal["image"]:
        """The type identifier for image groups."""
        raise NotImplementedError()



class AsyncImageGroup(BaseAsyncGroup[ImageChunk, Image]):
    """Async group for streaming image content chunks."""

    @property
    def type(self) -> Literal["image"]:
        """The type identifier for image groups."""
        raise NotImplementedError()

