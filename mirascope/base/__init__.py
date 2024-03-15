"""Base modules for the Mirascope library."""
from .calls import BaseCall
from .extractors import BaseExtractor, ExtractedType
from .prompts import BasePrompt, tags
from .tools import BaseTool, BaseType
from .types import (
    BaseCallParams,
    BaseCallResponse,
    BaseCallResponseChunk,
    Message,
)
from .utils import (
    convert_base_model_to_tool,
    convert_base_type_to_tool,
    convert_function_to_tool,
    tool_fn,
)
