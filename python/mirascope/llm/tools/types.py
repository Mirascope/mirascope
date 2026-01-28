"""Type aliases for tool parameter types used in provider signatures."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeAlias
from typing_extensions import TypeAliasType

from ..context import DepsT
from .provider_tools import ProviderTool
from .tool_schema import AnyToolSchema
from .toolkit import (
    AsyncContextToolkit,
    AsyncToolkit,
    BaseToolkit,
    ContextToolkit,
    Toolkit,
)
from .tools import AsyncContextTool, AsyncTool, ContextTool, Tool

AnyTools: TypeAlias = (
    Sequence[AnyToolSchema | ProviderTool] | BaseToolkit[AnyToolSchema]
)

Tools: TypeAlias = Sequence[Tool | ProviderTool] | Toolkit
"""Type alias for sync tool parameters: a sequence of Tools or a Toolkit."""

AsyncTools: TypeAlias = Sequence[AsyncTool | ProviderTool] | AsyncToolkit
"""Type alias for async tool parameters: a sequence of AsyncTools or an AsyncToolkit."""

ContextTools = TypeAliasType(
    "ContextTools",
    Sequence[Tool | ContextTool[DepsT] | ProviderTool] | ContextToolkit[DepsT],
    type_params=(DepsT,),
)
"""Type alias for sync context tool parameters: a sequence of Tools/ContextTools or a ContextToolkit."""

AsyncContextTools = TypeAliasType(
    "AsyncContextTools",
    Sequence[AsyncTool | AsyncContextTool[DepsT] | ProviderTool]
    | AsyncContextToolkit[DepsT],
    type_params=(DepsT,),
)
"""Type alias for async context tool parameters: a sequence of AsyncTools/AsyncContextTools or an AsyncContextToolkit."""


def normalize_tools(tools: Tools | None) -> Toolkit:
    """Normalize tools input to a Toolkit.

    Args:
        tools: A sequence of Tools, a Toolkit, or None.

    Returns:
        A Toolkit containing the tools (or an empty Toolkit if None).
    """
    if tools is None:
        return Toolkit(None)
    if isinstance(tools, Toolkit):
        return tools
    return Toolkit(tools)


def normalize_async_tools(tools: AsyncTools | None) -> AsyncToolkit:
    """Normalize async tools input to an AsyncToolkit.

    Args:
        tools: A sequence of AsyncTools, an AsyncToolkit, or None.

    Returns:
        An AsyncToolkit containing the tools (or an empty AsyncToolkit if None).
    """
    if tools is None:
        return AsyncToolkit(None)
    if isinstance(tools, AsyncToolkit):
        return tools
    return AsyncToolkit(tools)


def normalize_context_tools(
    tools: ContextTools[DepsT] | None,
) -> ContextToolkit[DepsT]:
    """Normalize context tools input to a ContextToolkit.

    Args:
        tools: A sequence of Tools/ContextTools, a ContextToolkit, or None.

    Returns:
        A ContextToolkit containing the tools (or an empty ContextToolkit if None).
    """
    if tools is None:
        return ContextToolkit(None)
    if isinstance(tools, ContextToolkit):
        return tools
    return ContextToolkit(tools)


def normalize_async_context_tools(
    tools: AsyncContextTools[DepsT] | None,
) -> AsyncContextToolkit[DepsT]:
    """Normalize async context tools input to an AsyncContextToolkit.

    Args:
        tools: A sequence of AsyncTools/AsyncContextTools, an AsyncContextToolkit, or None.

    Returns:
        An AsyncContextToolkit containing the tools (or an empty AsyncContextToolkit if None).
    """
    if tools is None:
        return AsyncContextToolkit(None)
    if isinstance(tools, AsyncContextToolkit):
        return tools
    return AsyncContextToolkit(tools)
