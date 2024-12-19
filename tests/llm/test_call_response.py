from typing import Any, cast

from mirascope.core.base import (
    BaseCallParams,
    BaseCallResponse,
    BaseDynamicConfig,
    BaseMessageParam,
    BaseTool,
    Metadata,
)
from mirascope.core.base.types import FinishReason
from mirascope.llm.call_response import CallResponse


class DummyCallParams(BaseCallParams):
    pass


class DummyMessageParam(BaseMessageParam):
    role: str
    content: Any


class DummyTool(BaseTool):
    def call(self): ...

    @property
    def model_fields(self):  # pyright: ignore [reportIncompatibleMethodOverride]
        return ["field1"]

    field1: str = "tool_field"


class DummyProviderCallResponse(
    BaseCallResponse[
        Any,
        DummyTool,
        Any,
        BaseDynamicConfig,
        DummyMessageParam,
        DummyCallParams,
        DummyMessageParam,
    ]
):
    @property
    def content(self) -> str:
        return "dummy_content"

    @property
    def finish_reasons(self) -> list[str] | None:
        return ["finish"]

    @property
    def model(self) -> str | None:
        return "dummy_model"

    @property
    def id(self) -> str | None: ...

    @property
    def usage(self) -> Any: ...

    @property
    def input_tokens(self) -> int | float | None: ...

    @property
    def output_tokens(self) -> int | float | None: ...

    @property
    def cost(self) -> float | None: ...

    @property
    def message_param(self) -> Any: ...

    @property
    def tools(self) -> list[DummyTool] | None:
        return [DummyTool()]

    @property
    def tool(self) -> DummyTool | None: ...

    @classmethod
    def tool_message_params(  # pyright: ignore [reportIncompatibleMethodOverride]
        cls, tools_and_outputs: list[tuple[DummyTool, str]]
    ) -> list[Any]: ...

    @property
    def common_finish_reasons(self) -> list[FinishReason] | None:
        return cast(list[FinishReason], self.finish_reasons)

    @property
    def common_message_param(self):
        return DummyMessageParam(role="assistant", content="common_message")

    @property
    def common_usage(self): ...

    def common_construct_call_response(self):
        return self

    def common_construct_message_param(
        self, tool_calls: list[Any] | None, content: str | None
    ): ...


def test_call_response():
    dummy_response = DummyProviderCallResponse(
        metadata=Metadata(),
        response={},
        tool_types=None,
        prompt_template=None,
        fn_args={},
        dynamic_config={},
        messages=[],
        call_params=DummyCallParams(),
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )
    call_response_instance = CallResponse(response=dummy_response)  # pyright: ignore [reportAbstractUsage]

    assert call_response_instance.finish_reasons == ["finish"]
    assert call_response_instance.message_param.role == "assistant"
    assert call_response_instance.tools is not None
    assert call_response_instance.tool is not None
    assert str(call_response_instance) == "dummy_content"
    assert call_response_instance._response.common_finish_reasons == ["finish"]
