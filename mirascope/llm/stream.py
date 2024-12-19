from __future__ import annotations

from typing import Any, Generic, TypeVar

from mirascope.core.base import (
    BaseCallKwargs,
    BaseCallParams,
    BaseCallResponse,
    BaseCallResponseChunk,
    BaseDynamicConfig,
    BaseMessageParam,
    BaseTool,
    Metadata,
)
from mirascope.core.base.stream import BaseStream
from mirascope.llm.call_response import CallResponse

_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound=BaseCallResponse)
_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", bound=BaseCallResponseChunk
)
_UserMessageParamT = TypeVar("_UserMessageParamT", bound=BaseMessageParam)
_AssistantMessageParamT = TypeVar("_AssistantMessageParamT", bound=BaseMessageParam)
_ToolMessageParamT = TypeVar("_ToolMessageParamT", bound=BaseMessageParam)
_MessageParamT = TypeVar("_MessageParamT", bound=BaseMessageParam)
_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_ToolSchemaT = TypeVar("_ToolSchemaT")
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_BaseCallParamsT = TypeVar("_BaseCallParamsT", bound=BaseCallParams)
_FinishReasonT = TypeVar("_FinishReasonT")


class Stream(
    BaseStream[
        _BaseCallResponseT,
        _BaseCallResponseChunkT,
        _UserMessageParamT,
        _AssistantMessageParamT,
        _ToolMessageParamT,
        _MessageParamT,
        _BaseToolT,
        _ToolSchemaT,
        _BaseDynamicConfigT,
        _BaseCallParamsT,
        _FinishReasonT,
    ],
    Generic[
        _BaseCallResponseT,
        _BaseCallResponseChunkT,
        _UserMessageParamT,
        _AssistantMessageParamT,
        _ToolMessageParamT,
        _MessageParamT,
        _BaseToolT,
        _ToolSchemaT,
        _BaseDynamicConfigT,
        _BaseCallParamsT,
        _FinishReasonT,
    ],
):
    """
    A non-pydantic class that inherits from BaseStream.

    This class:
    - Inherits BaseStream
    - Does not use BaseProviderConverter
    - Calls `_response.common_...` methods/properties if `_response` is available
      (In this example, we assume _response is set somehow or common methods are directly implemented)
    """

    def __init__(
        self,
        *,
        stream: Any,  # noqa: ANN401
        metadata: Metadata,
        tool_types: list[type[_BaseToolT]] | None,
        call_response_type: type[_BaseCallResponseT],
        model: str,
        prompt_template: str | None,
        fn_args: dict[str, Any],
        dynamic_config: _BaseDynamicConfigT,
        messages: list[_MessageParamT],
        call_params: _BaseCallParamsT,
        call_kwargs: BaseCallKwargs[_ToolSchemaT],
    ) -> None:
        super().__init__(
            stream=stream,
            metadata=metadata,
            tool_types=tool_types,
            call_response_type=call_response_type,
            model=model,
            prompt_template=prompt_template,
            fn_args=fn_args,
            dynamic_config=dynamic_config,
            messages=messages,
            call_params=call_params,
            call_kwargs=call_kwargs,
        )

    def common_construct_call_response(self) -> CallResponse:
        """A common method that constructs a CallResponse instance."""
        return CallResponse(response=self.construct_call_response())  # pyright: ignore [reportAbstractUsage]
