from __future__ import annotations

import inspect
from abc import ABC
from typing import ClassVar, Generic, TypeVar, cast

from pydantic import BaseModel, ConfigDict, create_model

from mirascope.core import BaseTool, BaseToolKit
from mirascope.core.base._utils import DEFAULT_TOOL_DOCSTRING


class _ConfigurableToolConfig(BaseModel, ABC):
    """Base configuration for tools"""

    @classmethod
    def from_env(cls: type[_ConfigurableToolConfigT]) -> _ConfigurableToolConfigT:
        """Returns a configuration instance from environment variables."""
        return cls()


_ConfigurableToolConfigT = TypeVar(
    "_ConfigurableToolConfigT", bound=_ConfigurableToolConfig
)

_ToolSchemaT = TypeVar("_ToolSchemaT")


class ConfigurableTool(BaseTool, Generic[_ConfigurableToolConfigT], ABC):
    """Abstract base class for configurable tools.

    Subclasses must define a `__prompt_usage_description__` class variable
    and __configurable_tool_config__ class variable with a subclass of _ToolConfig.
    """

    __configurable_tool_config__: ClassVar[_ConfigurableToolConfig]
    __prompt_usage_description__: ClassVar[str]
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def _get_config(cls) -> _ConfigurableToolConfigT:
        """Get tool configuration"""
        return cast(_ConfigurableToolConfigT, cls.__configurable_tool_config__)

    @classmethod
    def from_config(
        cls: type[_ConfigurableToolT], config: _ConfigurableToolConfigT
    ) -> type[_ConfigurableToolT]:
        """Create tool class with custom configuration"""

        # ClassVar cannot get TypeVar Type. So, we need the comment to ignore the error.
        config = cls._get_config().model_validate(config)  # pyright: ignore [reportAssignmentType]
        new_model = create_model(
            cls.__name__,
            __base__=cls,
            __module__=cls.__module__,
            __doc__=cls.__doc__ if cls.__doc__ else DEFAULT_TOOL_DOCSTRING,
        )
        new_model.__prompt_usage_description__ = cls.__prompt_usage_description__
        new_model.__configurable_tool_config__ = config
        return new_model

    @classmethod
    def usage_description(cls) -> str:
        """Returns instructions for using this tool."""
        return inspect.cleandoc(cls.__prompt_usage_description__)


_ConfigurableToolT = TypeVar("_ConfigurableToolT", bound=ConfigurableTool)


class ConfigurableToolKit(BaseToolKit, Generic[_ConfigurableToolConfigT], ABC):
    """Abstract base class for configurable toolkit.

    Subclasses must define a `__prompt_usage_description__` class variable
    and __config__ class variable with a subclass of _ToolConfig.
    """

    config: _ConfigurableToolConfigT
    __prompt_usage_description__: ClassVar[str]
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def create_tools(self) -> list[type[BaseTool]]:
        """The method to create the tools."""
        return [
            tool.from_config(self.config)
            if issubclass(tool, ConfigurableTool) and "config" in self.model_fields_set
            else tool
            for tool in super().create_tools()
        ]

    @classmethod
    def usage_description(cls) -> str:
        """Returns instructions for using this toolkit."""
        return inspect.cleandoc(cls.__prompt_usage_description__)


_ConfigurableToolKitT = TypeVar("_ConfigurableToolKitT", bound=ConfigurableToolKit)
