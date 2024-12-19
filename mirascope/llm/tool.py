from __future__ import annotations

from typing import Any, TypeVar

from pydantic._internal._model_construction import ModelMetaclass

from mirascope.core.base.tool import BaseTool

_ToolResponseT = TypeVar("_ToolResponseT", bound=BaseTool)


class _DelegateAbstractMethodsForTool(ModelMetaclass):
    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,
    ) -> type:
        cls = super().__new__(mcls, name, bases, namespace)
        cls.__abstractmethods__ = frozenset()
        return cls


class Tool(BaseTool, metaclass=_DelegateAbstractMethodsForTool):
    """
    A provider-agnostic Tool class.
    - No BaseProviderConverter
    - Relies on _response having `common_` methods/properties if needed.
    """

    _response: BaseTool

    def __init__(self, response: BaseTool) -> None:
        super().__init__(
            **{field: getattr(response, field) for field in response.model_fields}
        )
        object.__setattr__(self, "_response", response)

    def __getattribute__(self, name: str) -> Any:
        special_names = {
            "_response",
            "provider",
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
            response = object.__getattribute__(self, "_response")
            return getattr(response, name)
        except AttributeError:
            return object.__getattribute__(self, name)
