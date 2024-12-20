import inspect
from typing import Any

from pydantic._internal._model_construction import ModelMetaclass


class _ResponseMetaclass(ModelMetaclass):
    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,  # noqa: ANN401
    ) -> type:
        cls = super().__new__(mcls, name, bases, namespace)
        cls.__abstractmethods__ = frozenset()
        cls._properties = [
            n
            for n, v in inspect.getmembers(cls)
            if isinstance(v, property)
            and not getattr(
                v.fget, "__isabstractmethod__", False
            )  # Use only properties that are not abstract
        ]

        return cls
