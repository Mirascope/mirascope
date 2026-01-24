"""Type aliases for tool parameter types used in provider signatures."""

from collections.abc import Sequence
from typing import TypeAlias
from typing_extensions import TypeAliasType

from ..context import DepsT
from .tool_schema import AnyToolSchema
from .toolkit import (
    AsyncContextToolkit,
    AsyncToolkit,
    BaseToolkit,
    ContextToolkit,
    Toolkit,
)
from .tools import AsyncContextTool, AsyncTool, ContextTool, Tool

AnyTools: TypeAlias = Sequence[AnyToolSchema] | BaseToolkit[AnyToolSchema]

Tools: TypeAlias = Sequence[Tool] | Toolkit
"""Type alias for sync tool parameters: a sequence of Tools or a Toolkit."""

AsyncTools: TypeAlias = Sequence[AsyncTool] | AsyncToolkit
"""Type alias for async tool parameters: a sequence of AsyncTools or an AsyncToolkit."""

ContextTools = TypeAliasType(
    "ContextTools",
    Sequence[Tool | ContextTool[DepsT]] | ContextToolkit[DepsT],
    type_params=(DepsT,),
)
"""Type alias for sync context tool parameters: a sequence of Tools/ContextTools or a ContextToolkit."""

AsyncContextTools = TypeAliasType(
    "AsyncContextTools",
    Sequence[AsyncTool | AsyncContextTool[DepsT]] | AsyncContextToolkit[DepsT],
    type_params=(DepsT,),
)
"""Type alias for async context tool parameters: a sequence of AsyncTools/AsyncContextTools or an AsyncContextToolkit."""
