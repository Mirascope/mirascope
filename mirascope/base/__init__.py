"""Base modules for the mirascope library."""
from .prompt import BasePrompt, format_template, tags
from .tools import (
    BaseTool,
    convert_base_model_to_tool,
    convert_base_type_to_tool,
    convert_function_to_tool,
    tool_fn,
)
from .types import (
    AssistantMessage,
    BaseCallParams,
    BaseType,
    Message,
    SystemMessage,
    ToolMessage,
    UserMessage,
    is_base_type,
)
