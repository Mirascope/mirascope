from __future__ import annotations

import inspect
import uuid
from abc import ABC
from typing import ClassVar, Generic, TypeVar, cast

from pydantic import BaseModel, ConfigDict, create_model

from mirascope.core import BaseTool, BaseToolKit
from mirascope.core.base.toolkit import is_toolkit_tool


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
        cls: type[_ConfigurableToolT], config: _ToolConfigT
    ) -> type[_ConfigurableToolT]:
        """Create tool class with custom configuration"""

        # ClassVar cannot get TypeVar Type. So, we need the comment to ignore the error.
        config = cls.__config__.model_validate(config)  # pyright: ignore [reportAssignmentType]
        new_model = create_model(
            cls.__name__,
            __base__=cls,
            __module__=cls.__module__,
        )
        new_model.__prompt_usage_description__ = cls.__prompt_usage_description__
        new_model.__config__ = config
        return new_model

    @classmethod
    def usage_description(cls) -> str:
        """Returns instructions for using this tool."""
        return inspect.cleandoc(cls.__prompt_usage_description__)


_ConfigurableToolT = TypeVar("_ConfigurableToolT", bound=ConfigurableTool)


class ConfigurableToolKit(BaseToolKit, Generic[_ToolConfigT], ABC):
    """Abstract base class for configurable toolkit.

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
        cls: type[_ConfigurableToolKitT], config: _ToolConfigT
    ) -> type[_ConfigurableToolKitT]:
        """Create tool class with custom configuration"""

        # ClassVar cannot get TypeVar Type. So, we need the comment to ignore the error.
        config = cls.__config__.model_validate(config)  # pyright: ignore [reportAssignmentType]
        new_model = create_model(
            cls.__name__,
            __base__=cls,
            __module__=cls.__module__,
            __namespace__=f"{cls.__namespace__}_{uuid.uuid4()}",
        )
        new_model.__prompt_usage_description__ = cls.__prompt_usage_description__
        new_model.__config__ = config

        for key in dir(new_model):
            attr = getattr(new_model, key)
            if not is_toolkit_tool(attr):
                continue
            attr.__config__ = config
        return new_model

    @classmethod
    def usage_description(cls) -> str:
        """Returns instructions for using this toolkit."""
        return inspect.cleandoc(cls.__prompt_usage_description__)


_ConfigurableToolKitT = TypeVar("_ConfigurableToolKitT", bound=ConfigurableToolKit)
