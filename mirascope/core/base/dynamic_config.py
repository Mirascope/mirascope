"""The base type in a function as an LLM call to return for dynamic configuration."""

from collections.abc import Callable, Sequence
from typing import Any, Generic, TypeVar

from typing_extensions import NotRequired, TypedDict

from .call_params import BaseCallParams
from .metadata import Metadata
from .tool import BaseTool

_MessageParamT = TypeVar("_MessageParamT", bound=Any)
_CallParamsT = TypeVar("_CallParamsT", bound=BaseCallParams)
_ClientT = TypeVar("_ClientT", bound=object)


class DynamicConfigBase(TypedDict):
    metadata: NotRequired[Metadata]
    computed_fields: NotRequired[dict[str, Any | list[Any] | list[list[Any]]]]
    tools: NotRequired[Sequence[type[BaseTool] | Callable]]


class DynamicConfigMessages(DynamicConfigBase, Generic[_MessageParamT]):
    messages: NotRequired[Sequence[_MessageParamT]]


class DynamicConfigCallParams(DynamicConfigBase, Generic[_CallParamsT]):
    call_params: NotRequired[_CallParamsT]


class DynamicConfigClient(DynamicConfigBase, Generic[_ClientT]):
    client: NotRequired[_ClientT | None]


class DynamicConfigMessagesCallParams(
    DynamicConfigBase, Generic[_MessageParamT, _CallParamsT]
):
    messages: NotRequired[Sequence[_MessageParamT]]
    call_params: NotRequired[_CallParamsT]


class DynamicConfigMessagesClient(DynamicConfigBase, Generic[_MessageParamT, _ClientT]):
    messages: NotRequired[Sequence[_MessageParamT]]
    client: NotRequired[_ClientT | None]


class DynamicConfigCallParamsClient(DynamicConfigBase, Generic[_CallParamsT, _ClientT]):
    call_params: NotRequired[_CallParamsT]
    client: NotRequired[_ClientT | None]


class DynamicConfigFull(
    DynamicConfigBase, Generic[_MessageParamT, _CallParamsT, _ClientT]
):
    messages: NotRequired[Sequence[_MessageParamT]]
    call_params: NotRequired[_CallParamsT]
    client: NotRequired[_ClientT | None]


BaseDynamicConfig = (
    DynamicConfigBase
    | DynamicConfigMessages[_MessageParamT]
    | DynamicConfigCallParams[_CallParamsT]
    | DynamicConfigClient[_ClientT]
    | DynamicConfigMessagesCallParams[_MessageParamT, _CallParamsT]
    | DynamicConfigMessagesClient[_MessageParamT, _ClientT]
    | DynamicConfigCallParamsClient[_CallParamsT, _ClientT]
    | DynamicConfigFull[_MessageParamT, _CallParamsT, _ClientT]
    | None
)
"""The base type in a function as an LLM call to return for dynamic configuration.

Attributes:
    metadata: Any metadata to include in call responses.
    computed_fields: Fields to be computed and injected into the prompt template at
        runtime.
    tools: Tools to be provided to the LLM API call at runtime.
    messages: Custom message parameters, which will override any other form of writing
        prompts when used.
    call_params: Call parameters to use when making the LLM API call.
    client: A custom client to use in place of the default client.
"""
