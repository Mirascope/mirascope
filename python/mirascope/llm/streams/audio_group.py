"""Audio group classes for streaming audio content."""

from typing import Literal

from ..content import Audio, AudioChunk
from .groups import BaseAsyncGroup, BaseGroup


class AudioGroup(BaseGroup[AudioChunk, Audio]):
    """Group for streaming audio content chunks."""

    @property
    def type(self) -> Literal["audio"]:
        """The type identifier for audio groups."""
        raise NotImplementedError()


class AsyncAudioGroup(BaseAsyncGroup[AudioChunk, Audio]):
    """Async group for streaming audio content chunks."""

    @property
    def type(self) -> Literal["audio"]:
        """The type identifier for audio groups."""
        raise NotImplementedError()
