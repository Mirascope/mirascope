"""Call response chunk module."""

from __future__ import annotations

from typing import Any

from ..core.base.call_response_chunk import BaseCallResponseChunk
from ..core.base.types import CostMetadata, FinishReason, Usage
from ._response_metaclass import _ResponseMetaclass


class CallResponseChunk(
    BaseCallResponseChunk[Any, FinishReason],
    metaclass=_ResponseMetaclass,
):
    _response: BaseCallResponseChunk[Any, Any]

    def __init__(
        self,
        response: BaseCallResponseChunk[Any, Any],
    ) -> None:
        super().__init__(
            **{field: getattr(response, field) for field in response.model_fields}
        )
        object.__setattr__(self, "_response", response)

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
            "_properties",
            "cost_metadata",
            "finish_reasons",
            "usage",
        } | set(object.__getattribute__(self, "_properties"))

        if name in special_names:
            return object.__getattribute__(self, name)

        try:
            response = object.__getattribute__(self, "_response")
            return getattr(response, name)
        except AttributeError:
            return object.__getattribute__(self, name)

    @property
    def finish_reasons(self) -> list[FinishReason] | None:
        return self._response.common_finish_reasons

    @property
    def usage(self) -> Usage | None:
        return self._response.common_usage

    @property
    def cost_metadata(self) -> CostMetadata:
        """Get metadata required for cost calculation."""

        return self._response.cost_metadata
