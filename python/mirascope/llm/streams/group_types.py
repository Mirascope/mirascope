"""Group type unions for streaming content."""

from typing import TypeAlias

from .audio_group import AsyncAudioGroup, AudioGroup
from .image_group import AsyncImageGroup, ImageGroup
from .text_group import AsyncTextGroup, TextGroup
from .thinking_group import AsyncThinkingGroup, ThinkingGroup
from .tool_call_group import AsyncToolCallGroup, ToolCallGroup

Group: TypeAlias = (
    TextGroup | ImageGroup | AudioGroup | ToolCallGroup | ThinkingGroup
)
"""Union type for all synchronous content groups."""

AsyncGroup: TypeAlias = (
    AsyncTextGroup | AsyncImageGroup | AsyncAudioGroup | AsyncToolCallGroup | AsyncThinkingGroup
)
"""Union type for all asynchronous content groups."""