from __future__ import annotations

import inspect
from abc import ABC
from typing import ClassVar, Generic, TypeVar, cast

from pydantic import BaseModel, ConfigDict, create_model

from mirascope.core import BaseTool


class _ToolConfig(BaseModel, ABC):
    """Base configuration for tools"""

    @classmethod
    def from_env(cls: type[_ToolConfigT]) -> _ToolConfigT:
        """Returns a configuration instance from environment variables."""
        return cls()


_ToolConfigT = TypeVar("_ToolConfigT", bound=_ToolConfig)

_ToolSchemaT = TypeVar("_ToolSchemaT")


class ConfigurableTool(
    BaseTool[_ToolSchemaT], Generic[_ToolConfigT, _ToolSchemaT], ABC
):
    """Abstract base class for configurable tools.

    Subclasses must define a `__prompt_usage_description__` class variable
    and __config__ class variable with a subclass of _ToolConfig.
    """

    __config__: ClassVar[_ToolConfig]
    __prompt_usage_description__: ClassVar[str]
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def _config(cls) -> _ToolConfigT:
        """Get tool configuration"""
        return cast(_ToolConfigT, cls.__config__)

    @classmethod
    def from_config(
        cls, config: _ToolConfigT
    ) -> type[ConfigurableTool[_ToolConfigT, _ToolSchemaT]]:
        """Create tool class with custom configuration"""

        # ClassVar cannot get TypeVar Type. So, we need the comment to ignore the error.
        config = cls.__config__.model_validate(config)  # pyright: ignore [reportAssignmentType]
        NewModel = create_model(
            cls.__name__,
            __base__=cls,
            __module__=cls.__module__,
        )
        NewModel.__prompt_usage_description__ = cls.__prompt_usage_description__
        NewModel.__config__ = config
        return NewModel

    @classmethod
    def usage_description(cls) -> str:
        """Returns instructions for using this tool."""
        return inspect.cleandoc(cls.__prompt_usage_description__)
