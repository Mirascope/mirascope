"""Tool class for the provider-agnostic tool."""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic._internal._model_construction import ModelMetaclass

from ..core.base.tool import BaseTool

_ToolResponseT = TypeVar("_ToolResponseT", bound=BaseTool)


class _DelegateAbstractMethodsForTool(ModelMetaclass):
    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,  # noqa: ANN401
    ) -> type:
        cls = super().__new__(mcls, name, bases, namespace)
        cls.__abstractmethods__ = frozenset()
        return cls


_ToolMessageParamT = TypeVar("_ToolMessageParamT")


class Tool(BaseTool, metaclass=_DelegateAbstractMethodsForTool):
    """
    A provider-agnostic Tool class.
    - No BaseProviderConverter
    - Relies on _response having `common_` methods/properties if needed.
    """

    _tool: BaseTool

    def __init__(self, tool: BaseTool) -> None:
        super().__init__(**{field: getattr(tool, field) for field in tool.model_fields})
        object.__setattr__(self, "_tool", tool)

    def __getattribute__(self, name: str) -> Any:  # noqa: ANN401
        special_names = {
            "_response",
            "__dict__",
            "__class__",
            "model_fields",
            "__annotations__",
            "__pydantic_validator__",
            "__pydantic_fields_set__",
            "__pydantic_extra__",
            "__pydantic_private__",
            "__class_getitem__",
        }

        if name in special_names:
            return object.__getattribute__(self, name)

        try:
            tool = object.__getattribute__(self, "_tool")
            return getattr(tool, name)
        except AttributeError:
            return object.__getattribute__(self, name)
