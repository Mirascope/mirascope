from functools import cached_property
from typing import Any, ClassVar, cast

from pydantic import computed_field

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
    def model(self) -> str | None: ...

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

    @computed_field
    @cached_property
    def message_param(self) -> Any: ...

    @computed_field
    @cached_property
    def tools(self) -> list[DummyTool] | None:
        return [DummyTool()]

    @computed_field
    @cached_property
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

    def common_construct_call_response(self): ...

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


def test_call_response_attribute_fallback_on_instance():
    # This test covers the try-except block in __getattribute__
    # by accessing an attribute that doesn't exist on _response but exists on CallResponse instance.
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
    # Add an attribute directly to the call_response_instance that _response doesn't have
    call_response_instance.custom_attr = "custom_value"  # pyright: ignore [reportAttributeAccessIssue]
    # Accessing this attribute should trigger the except AttributeError block
    assert call_response_instance.custom_attr == "custom_value"


def test_tool_message_params_various_tool_call_ids_with_annotations():
    class ToolCallWithID:
        id = "tool_call_with_id"

    class ToolWithID(BaseTool):
        tool_call: ClassVar[Any] = ToolCallWithID()

        def call(self): ...
        @property
        def model_fields(self): ...  # pyright: ignore [reportIncompatibleMethodOverride]

        field1: str = "tool_field"

    class ToolNoCall(BaseTool):
        tool_call: ClassVar[Any] = None

        def call(self): ...
        @property
        def model_fields(self): ...  # pyright: ignore [reportIncompatibleMethodOverride]

        field1: str = "tool_field"

    class ToolCallNoIDClass:
        pass

    class ToolCallNoID(BaseTool):
        tool_call: ClassVar[Any] = ToolCallNoIDClass()  # no id attribute

        def call(self): ...
        @property
        def model_fields(self): ...  # pyright: ignore [reportIncompatibleMethodOverride]

        field1: str = "tool_field"

    tool_with_id = ToolWithID()
    tool_no_call = ToolNoCall()
    tool_call_no_id = ToolCallNoID()

    result_with_id = CallResponse.tool_message_params([(tool_with_id, "output1")])
    assert result_with_id[0].content[0].id == "tool_call_with_id"

    result_no_call = CallResponse.tool_message_params([(tool_no_call, "output2")])
    assert result_no_call[0].content[0].id is None

    result_no_id = CallResponse.tool_message_params([(tool_call_no_id, "output3")])
    assert result_no_id[0].content[0].id is None
