from collections.abc import Awaitable
from typing import Any

from typing_extensions import TypeVar

from ..content import ToolOutput
from ..types import Jsonable
from .async_context_tool import AsyncContextTool
from .async_tool import AsyncTool
from .context_tool import ContextTool
from .tool import Tool

SyncToolReturnT = TypeVar(
    "SyncToolReturnT",
    bound=Jsonable,
)
AsyncToolReturnT = TypeVar(
    "AsyncToolReturnT",
    bound=Jsonable,
)

ToolOutputT = TypeVar(
    "ToolOutputT",
    bound=ToolOutput | Awaitable[ToolOutput],
)

ToolT = TypeVar(
    "ToolT",
    bound=Tool[..., Jsonable] | AsyncTool[..., Jsonable],
    covariant=True,
)
ContextToolT = TypeVar(
    "ContextToolT",
    bound=Tool[..., Jsonable]
    | ContextTool[..., Jsonable, Any]
    | AsyncTool[..., Jsonable]
    | AsyncContextTool[..., Jsonable, Any],
    covariant=True,
)

T = TypeVar("T", bound=Jsonable, covariant=True)
AT = TypeVar("AT", bound=Jsonable, covariant=True)
