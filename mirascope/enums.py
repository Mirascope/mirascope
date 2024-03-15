"""Enum Classes for mirascope."""
from enum import Enum, EnumMeta
from typing import Any


class _Metaclass(EnumMeta):
    """Base `EnumMeta` subclass for accessing enum members directly."""

    def __getattribute__(cls, __name: str) -> Any:
        value = super().__getattribute__(__name)
        if isinstance(value, Enum):
            value = value.value
        return value


class _Enum(str, Enum, metaclass=_Metaclass):
    """Base Enum Class."""


class MirascopeCommand(_Enum):
    """CLI commands to be executed.

    - ADD: save a modified prompt to the `versions/` folder.
    - USE: load a specific version of the prompt from `versions/` as the current prompt.
    - STATUS: display if any changes have been made to prompts, and if a prompt is
        specified, displays changes for only said prompt.
    - INIT: initializes the necessary folders for prompt versioning with CLI.
    """

    ADD = "add"
    USE = "use"
    STATUS = "status"
    INIT = "init"


class MessageRole(_Enum):
    """Roles that the `BasePrompt` messages parser can parse from the template.

    SYSTEM: A system message.
    USER: A user message.
    ASSISTANT: A message response from the assistant or chat client.
    MODEL: A message response from the assistant or chat client. Model is used by
        Google's Gemini instead of assistant, which doesn't have system messages.
    TOOL: A message representing the output of calling a tool.
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    MODEL = "model"
    TOOL = "tool"
