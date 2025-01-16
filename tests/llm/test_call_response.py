from functools import cached_property
from typing import Any, ClassVar, cast
from unittest.mock import PropertyMock, patch

import pytest
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
from mirascope.llm.tool import Tool


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
        return [BaseMessageParam(role="assistant", content="common_message")]

    @property
    def common_usage(self): ...

    def common_construct_call_response(self): ...

    def common_construct_message_param(
        self, tool_calls: list[Any] | None, content: str | None
    ): ...


@pytest.fixture
def dummy_call_response_instance():
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
    return CallResponse(response=dummy_response)  # pyright: ignore [reportAbstractUsage]


def test_call_response(dummy_call_response_instance):
    assert dummy_call_response_instance.finish_reasons == ["finish"]
    assert isinstance(dummy_call_response_instance.message_param, list)
    message_param = dummy_call_response_instance.message_param[0]
    assert message_param.role == "assistant"
    assert dummy_call_response_instance.tools is not None
    assert dummy_call_response_instance.tool is not None
    assert str(dummy_call_response_instance) == "dummy_content"
    assert dummy_call_response_instance._response.common_finish_reasons == ["finish"]


def test_call_response_attribute_fallback_on_instance(dummy_call_response_instance):
    dummy_call_response_instance.custom_attr = "custom_value"  # pyright: ignore [reportAttributeAccessIssue]
    assert dummy_call_response_instance.custom_attr == "custom_value"


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


@pytest.mark.asyncio
async def test_tool_property_returns_first_tool(dummy_call_response_instance):
    first_tool = Tool(tool=DummyTool())  # pyright: ignore [reportAbstractUsage]

    with patch.object(
        type(dummy_call_response_instance._response),
        "common_tools",
        new_callable=PropertyMock,
    ) as mock_common_tools:
        mock_common_tools.return_value = [first_tool]

        assert (
            dummy_call_response_instance.tool == first_tool
        ), "Expected the first Tool in _response.common_tools"


@pytest.mark.asyncio
async def test_tool_returns_none_when_no_tools(dummy_call_response_instance):
    with patch.object(
        type(dummy_call_response_instance._response),
        "common_tools",
        new_callable=PropertyMock,
    ) as mock_common_tools:
        mock_common_tools.return_value = None

        assert (
            dummy_call_response_instance.tool is None
        ), "Expected None when _response.common_tools is None"
