"""The base function return type for functions as LLM calls."""

from typing import Any, Callable, Generic, TypeVar

from typing_extensions import NotRequired, TypedDict

from .call_params import BaseCallParams
from .tools import BaseTool

_MessageParamT = TypeVar("_MessageParamT", bound=Any)
_CallParamsT = TypeVar("_CallParamsT", bound=BaseCallParams)


class FunctionReturnBase(TypedDict):
    computed_fields: NotRequired[dict[str, str | list[str] | list[list[str]]]]
    tools: NotRequired[list[type[BaseTool] | Callable]]


class FunctionReturnMessages(FunctionReturnBase, Generic[_MessageParamT]):
    messages: NotRequired[list[_MessageParamT]]


class FunctionReturnCallParams(FunctionReturnBase, Generic[_CallParamsT]):
    call_params: NotRequired[_CallParamsT]


class FunctionReturnFull(FunctionReturnBase, Generic[_MessageParamT, _CallParamsT]):
    messages: NotRequired[list[_MessageParamT]]
    call_params: NotRequired[_CallParamsT]


BaseFunctionReturn = (
    FunctionReturnBase
    | FunctionReturnMessages[_MessageParamT]
    | FunctionReturnCallParams[_CallParamsT]
    | FunctionReturnFull[_MessageParamT, _CallParamsT]
    | None
)
"""The base function return type for functions as LLM calls."""
