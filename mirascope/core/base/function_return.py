"""The base function return type for functions as LLM calls."""

from typing import Any, Generic, TypeVar

from typing_extensions import NotRequired, TypedDict

from .call_params import BaseCallParams
from .tools import BaseTool

MessageParamT = TypeVar("MessageParamT", bound=Any)
CallParamsT = TypeVar("CallParamsT", bound=BaseCallParams)


class FunctionReturnBase(TypedDict):
    computed_fields: NotRequired[dict[str, str | list[str] | list[list[str]]]]
    tools: NotRequired[list[type[BaseTool]]]


class FunctionReturnMessages(FunctionReturnBase, Generic[MessageParamT]):
    messages: NotRequired[list[MessageParamT]]


class FunctionReturnCallParams(FunctionReturnBase, Generic[CallParamsT]):
    call_params: NotRequired[CallParamsT]


class FunctionReturnFull(FunctionReturnBase, Generic[MessageParamT, CallParamsT]):
    messages: NotRequired[list[MessageParamT]]
    call_params: NotRequired[CallParamsT]


BaseFunctionReturn = (
    FunctionReturnBase
    | FunctionReturnMessages[MessageParamT]
    | FunctionReturnCallParams[CallParamsT]
    | FunctionReturnFull[MessageParamT, CallParamsT]
    | None
)
"""The base function return type for functions as LLM calls."""
