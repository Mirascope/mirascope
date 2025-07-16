from typing import Any

from typing_extensions import TypeVar

from ..types import Jsonable
from .async_context_tool import AsyncContextTool
from .async_tool import AsyncTool
from .context_tool import ContextTool
from .tool import Tool

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


ToolReturnT = TypeVar("ToolReturnT", bound=Jsonable, covariant=True)
AsyncToolReturnT = TypeVar("AsyncToolReturnT", bound=Jsonable, covariant=True)
