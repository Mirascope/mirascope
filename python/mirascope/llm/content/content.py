from typing import TypeAlias

from .audios.audio import Audio
from .documents.document import Document
from .images.image import Image
from .texts.text import Text
from .thinking.thinking import Thinking
from .tools.tool_call import ToolCall
from .tools.tool_output import ToolOutput

Content: TypeAlias = Text | Image | Audio | Document | ToolCall | ToolOutput | Thinking
"""Content types that can be included in messages."""
