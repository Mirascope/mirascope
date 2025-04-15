from collections.abc import Sequence
from functools import cached_property
from typing import Any, ClassVar, cast
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from pydantic import computed_field

from mirascope.core.base import (
    BaseCallParams,
    BaseCallResponse,
    BaseDynamicConfig,
    BaseMessageParam,
    BaseTool,
    Metadata,
    ToolResultPart,
    Usage,
)
from mirascope.core.base._utils import BaseMessageParamConverter
from mirascope.core.base.types import CostMetadata, FinishReason
from mirascope.llm.call_response import CallResponse
from mirascope.llm.tool import Tool


class DummyCallParams(BaseCallParams):
    pass


class DummyMessageParam(BaseMessageParam):
    role: str
    content: Any


class DummyTool(Tool):
    def call(self): ...

    @property
    def model_fields(self):  # pyright: ignore [reportIncompatibleVariableOverride]
        return ["field1"]

    field1: str = "tool_field"


class DummyMessageParamConverter(BaseMessageParamConverter):
    @staticmethod
    def from_provider(message_params: list[Any]) -> list[BaseMessageParam]:
        return [
            BaseMessageParam(role=message_param.role, content=message_param.content)
            for message_param in message_params
        ]

    @staticmethod
    def to_provider(message_params: list[BaseMessageParam]) -> list[Any]: ...


class DummyProviderCallResponse(
    BaseCallResponse[
        Any,
        DummyTool,
        Any,
        BaseDynamicConfig,
        DummyMessageParam,
        DummyCallParams,
        DummyMessageParam,
        Any,
    ]
):
    _message_converter: type = DummyMessageParamConverter

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
    def cached_tokens(self) -> int | float | None: ...

    @property
    def output_tokens(self) -> int | float | None: ...

    @property
    def cost(self) -> float | None: ...

    @computed_field
    @cached_property
    def message_param(self) -> Any: ...

    @cached_property
    def tools(self) -> list[DummyTool] | None:
        return [DummyTool(MagicMock(spec=BaseTool))]

    @cached_property
    def tool(self) -> DummyTool | None: ...

    @classmethod
    def tool_message_params(  # pyright: ignore [reportIncompatibleMethodOverride]
        cls, tools_and_outputs: Sequence[tuple[DummyTool, str]]
    ) -> list[Any]: ...

    @property
    def common_finish_reasons(self) -> list[FinishReason] | None:
        return cast(list[FinishReason], self.finish_reasons)

    @property
    def common_message_param(self):
        return BaseMessageParam(role="assistant", content="common_message")

    @property
    def common_user_message_param(self):
        return BaseMessageParam(role="user", content="common_user_message")

    @property
    def common_usage(self) -> Usage | None:
        return Usage(input_tokens=1, cached_tokens=1, output_tokens=1, total_tokens=2)

    def common_construct_call_response(self): ...

    def common_construct_message_param(
        self, tool_calls: list[Any] | None, content: str | None
    ): ...

    @property
    def cost_metadata(self) -> CostMetadata: ...


@pytest.fixture
def dummy_call_response_instance():
    dummy_response = DummyProviderCallResponse(
        metadata=Metadata(),
        response={},
        tool_types=None,
        prompt_template=None,
        fn_args={},
        dynamic_config={},
        messages=[DummyMessageParam(role="assistant", content="message")],
        call_params=DummyCallParams(),
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )
    return CallResponse(response=dummy_response)  # pyright: ignore [reportAbstractUsage,reportArgumentType]


def test_call_response(dummy_call_response_instance):
    assert dummy_call_response_instance.finish_reasons == ["finish"]
    assert isinstance(dummy_call_response_instance.message_param, BaseMessageParam)
    message_param = dummy_call_response_instance.message_param
    assert message_param.role == "assistant"
    assert dummy_call_response_instance.tools is not None
    assert dummy_call_response_instance.tool is not None
    assert str(dummy_call_response_instance) == "dummy_content"
    assert dummy_call_response_instance._response.common_finish_reasons == ["finish"]
    assert dummy_call_response_instance.usage == Usage(
        input_tokens=1, cached_tokens=1, output_tokens=1, total_tokens=2
    )
    assert dummy_call_response_instance.common_messages == [
        BaseMessageParam(role="assistant", content="message")
    ]
    assert dummy_call_response_instance.messages == [
        BaseMessageParam(role="assistant", content="message")
    ]


def test_call_response_attribute_fallback_on_instance(dummy_call_response_instance):
    dummy_call_response_instance.custom_attr = "custom_value"  # pyright: ignore [reportAttributeAccessIssue]
    assert dummy_call_response_instance.custom_attr == "custom_value"


def test_tool_message_params_various_tool_call_ids_with_annotations():
    class ToolCallWithID:
        id = "tool_call_with_id"

    class ToolWithID(Tool):
        tool_call: ClassVar[Any] = ToolCallWithID()

        def call(self): ...
        @property
        def model_fields(self): ...  # pyright: ignore [reportIncompatibleVariableOverride]

        field1: str = "tool_field"

    class ToolNoCall(Tool):
        def call(self): ...
        @property
        def model_fields(self): ...  # pyright: ignore [reportIncompatibleVariableOverride]

        field1: str = "tool_field"

    class ToolCallNoIDClass:
        pass

    class ToolCallNoID(Tool):
        tool_call: ClassVar[Any] = ToolCallNoIDClass()  # no id attribute

        def call(self): ...
        @property
        def model_fields(self): ...  # pyright: ignore [reportIncompatibleVariableOverride]

        field1: str = "tool_field"

    mock_tool = MagicMock(spec=BaseTool)
    mock_tool._name.return_value = "tool_name"
    tool_with_id = ToolWithID(mock_tool)
    tool_no_call = ToolNoCall(mock_tool)
    tool_call_no_id = ToolCallNoID(mock_tool)

    result_with_id = CallResponse.tool_message_params([(tool_with_id, "output1")])
    assert isinstance(result_with_id[0].content[0], ToolResultPart)
    assert result_with_id[0].content[0].id == "tool_call_with_id"

    result_no_call = CallResponse.tool_message_params([(tool_no_call, "output2")])
    assert isinstance(result_no_call[0].content[0], ToolResultPart)
    assert result_no_call[0].content[0].id is None

    result_no_id = CallResponse.tool_message_params([(tool_call_no_id, "output3")])
    assert isinstance(result_no_id[0].content[0], ToolResultPart)
    assert result_no_id[0].content[0].id is None


@pytest.mark.asyncio
async def test_tool_property_returns_first_tool(dummy_call_response_instance):
    first_tool = Tool(tool=DummyTool(MagicMock(spec=BaseTool)))  # pyright: ignore [reportAbstractUsage]

    with patch.object(
        type(dummy_call_response_instance._response),
        "common_tools",
        new_callable=PropertyMock,
    ) as mock_common_tools:
        mock_common_tools.return_value = [first_tool]

        assert dummy_call_response_instance.tool == first_tool, (
            "Expected the first Tool in _response.common_tools"
        )


@pytest.mark.asyncio
async def test_tool_returns_none_when_no_tools(dummy_call_response_instance):
    with patch.object(
        type(dummy_call_response_instance._response),
        "common_tools",
        new_callable=PropertyMock,
    ) as mock_common_tools:
        mock_common_tools.return_value = None

        assert dummy_call_response_instance.tool is None, (
            "Expected None when _response.common_tools is None"
        )
