from typing import Generic, TypeVar

from pydantic import ConfigDict

from mirascope.core.base.tool import BaseTool

ToolMessageParamT = TypeVar("ToolMessageParamT")


class Tool(BaseTool, Generic[ToolMessageParamT]):
    """
    A generic tool class with a single type parameter representing the message param type.

    Example:
    Tool[ChatCompletionToolMessageParam]
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
