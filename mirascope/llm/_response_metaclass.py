import inspect
from functools import cached_property
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
        cls._properties = []

        for n, v in inspect.getmembers(cls):
            if isinstance(v, property):
                f = v.fget
            elif isinstance(v, cached_property):
                f = v.func
            else:
                continue

            if not getattr(f, "__isabstractmethod__", False):
                cls._properties.append(n)

        return cls
