from collections.abc import Callable

from pydantic import BaseModel, ConfigDict

from ...core.base import BaseTool


class BaseCallParams(BaseModel):
    """The parameters with which to make a call."""

    model: str
    tools: list[type[BaseTool] | Callable] | None = None

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)
