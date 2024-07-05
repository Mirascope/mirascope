"""The base type in a function as an LLM call to return for dynamic configuration."""

from typing import Any, Callable, Generic, TypeVar

from typing_extensions import NotRequired, TypedDict

from .call_params import BaseCallParams
from .metadata import Metadata
from .tool import BaseTool

_MessageParamT = TypeVar("_MessageParamT", bound=Any)
_CallParamsT = TypeVar("_CallParamsT", bound=BaseCallParams)


class DynamicConfigBase(TypedDict):
    metadata: NotRequired[Metadata]
    computed_fields: NotRequired[dict[str, Any | list[Any] | list[list[Any]]]]
    tools: NotRequired[list[type[BaseTool] | Callable]]


class DynamicConfigMessages(DynamicConfigBase, Generic[_MessageParamT]):
    messages: NotRequired[list[_MessageParamT]]


class DynamicConfigCallParams(DynamicConfigBase, Generic[_CallParamsT]):
    call_params: NotRequired[_CallParamsT]


class DynamicConfigFull(DynamicConfigBase, Generic[_MessageParamT, _CallParamsT]):
    messages: NotRequired[list[_MessageParamT]]
    call_params: NotRequired[_CallParamsT]


BaseDynamicConfig = (
    DynamicConfigBase
    | DynamicConfigMessages[_MessageParamT]
    | DynamicConfigCallParams[_CallParamsT]
    | DynamicConfigFull[_MessageParamT, _CallParamsT]
    | None
)
"""The base type in a function as an LLM call to return for dynamic configuration."""
