from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, Generic, TypeVar, cast

from pydantic import BaseModel, ConfigDict, create_model

from mirascope.core import BaseTool


class _ToolConfig(BaseModel, ABC):
    """Base configuration for tools"""

    @classmethod
    @abstractmethod
    def from_env(cls) -> _ToolConfig:
        """Load configuration from environment variables"""

    @classmethod
    def override_defaults(cls, config: _ToolConfig) -> _ToolConfig:
        """Create config with overridden default values"""
        return cls.model_validate(config)


ConfigT = TypeVar("ConfigT", bound=_ToolConfig)

_ToolSchemaT = TypeVar("_ToolSchemaT")


class ConfigurableTool(BaseTool[_ToolSchemaT], Generic[ConfigT, _ToolSchemaT], ABC):
    """
    Abstract base class for configurable tools.

    Subclasses must define a `__prompt_usage_description__` class variable
    and __config__ class variable with a subclass of _ToolConfig.
    """

    __config__: ClassVar[_ToolConfig]
    __prompt_usage_description__: ClassVar[str]
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def _config(cls) -> ConfigT:
        """Get tool configuration"""
        return cast(ConfigT, cls.__config__)

    @classmethod
    def from_config(cls, config: _ToolConfig) -> type[ConfigurableTool]:
        """Create tool class with custom configuration"""
        config = cls.__config__.override_defaults(config)
        NewModel = create_model(
            cls.__name__,
            __base__=cls,
            __module__=cls.__module__,
        )
        NewModel.__prompt_usage_description__ = cls.__prompt_usage_description__
        NewModel.__config__ = config
        return NewModel

    @classmethod
    def _get_base_system_prompt(cls) -> list[str]:
        """Get base system prompt structure"""
        return [
            "SYSTEM:",
            "You are an expert tool user. Your task is to solve user queries using the provided tools.",
            "",
            "You have access to the following tools:",
            f"- `{cls._name()}`: {cls._description()}",
        ]

    @classmethod
    def _add_usage_instructions(cls, prompt: list[str]) -> list[str]:
        """Add tool usage instructions to the prompt"""
        new_prompt = prompt.copy()
        if cls.__prompt_usage_description__:
            new_prompt.extend(
                [
                    "   ",
                    "    " + cls.__prompt_usage_description__.replace("\n", "\n    "),
                ]
            )
        return new_prompt

    @classmethod
    def get_prompt_instructions(cls) -> str:
        """Generate system prompt for LLM with tool usage instructions"""
        prompt = cls._get_base_system_prompt()
        prompt = cls._add_usage_instructions(prompt)
        return "\n".join(prompt)
