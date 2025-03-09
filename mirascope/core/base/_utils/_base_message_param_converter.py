"""Contains the BaseMessageParamConverter class."""

from abc import ABC, abstractmethod
from typing import Any

from mirascope.core.base.message_param import BaseMessageParam


class BaseMessageParamConverter(ABC):
    """Base class for converting message params to/from provider formats."""

    @staticmethod
    @abstractmethod
    def to_provider(message_params: list[BaseMessageParam]) -> list[Any]:
        """Converts base message params -> provider-specific messages."""
        pass

    @staticmethod
    @abstractmethod
    def from_provider(message_params: list[Any]) -> list[BaseMessageParam]:
        """Converts provider-specific messages -> Base message params."""
        pass
