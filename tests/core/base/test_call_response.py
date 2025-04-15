"""Tests the `call_response` module."""

import base64
import json
from collections.abc import Sequence
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from mirascope.core.base._utils import BaseMessageParamConverter
from mirascope.core.base.call_response import BaseCallResponse, transform_tool_outputs
from mirascope.core.base.message_param import BaseMessageParam


def test_base_call_response() -> None:
    """Tests the `BaseCallResponse` class."""

    class MyMessageParamConverter(BaseMessageParamConverter):
        @staticmethod
        def from_provider(message_params: list[dict]) -> list[BaseMessageParam]:
            """Converts provider-specific messages -> Base message params."""
            return [
                BaseMessageParam(
                    role=message_param["role"], content=message_param["content"]
                )
                for message_param in message_params
            ]

    class MyCallResponse(BaseCallResponse):
        _message_converter: type[MyMessageParamConverter] = MyMessageParamConverter

        @property
        def content(self) -> str:
            return "content"

    patch.multiple(MyCallResponse, __abstractmethods__=set()).start()
    call_response = MyCallResponse(
        metadata={},
        response="",
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[{"role": "user", "content": "content"}],
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )  # type: ignore
    assert str(call_response) == "content"
    tool = MagicMock()
    tool._name = lambda: "mock_tool"
    assert call_response.serialize_tool_types([tool], info=MagicMock()) == [
        {"type": "function", "name": "mock_tool"}
    ]
    assert call_response.common_tools is None
    assert call_response.common_usage is None
    assert call_response.common_messages == [
        BaseMessageParam(role="user", content="content")
    ]


def test_base_call_response_without_model() -> None:
    """Tests the `BaseCallResponse` class without model."""

    class MyCallResponse(BaseCallResponse):
        @property
        def content(self) -> str:
            return "content"

    patch.multiple(MyCallResponse, __abstractmethods__=set()).start()
    call_response = MyCallResponse(
        metadata={},
        response="",
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
        _model=None,  # pyright: ignore [reportArgumentType]
    )  # type: ignore
    assert str(call_response) == "content"
    tool = MagicMock()
    tool._name = lambda: "mock_tool"
    assert call_response.serialize_tool_types([tool], info=MagicMock()) == [
        {"type": "function", "name": "mock_tool"}
    ]
    assert call_response.common_tools is None
    assert call_response.common_usage is None
    assert call_response.cost is None


class SimpleModel(BaseModel):
    name: str
    value: int


class NestedModel(BaseModel):
    simple: SimpleModel
    values: list[int]


@pytest.fixture
def process_tools():
    @transform_tool_outputs
    def _process_tools(
        cls: Any, tools_and_outputs: Sequence[tuple[Any, str]]
    ) -> list[str]:
        return [output for _, output in tools_and_outputs]

    return _process_tools


@pytest.mark.parametrize(
    "input_value,expected",
    [
        ("string value", "string value"),
        (42, "42"),
        (3.14, "3.14"),
        (True, "true"),
        (b"binary data", base64.b64encode(b"binary data").decode("utf-8")),
    ],
)
def test_transform_tool_outputs_primitive_types(
    process_tools: Any, input_value: Any, expected: str
) -> None:
    tool = MagicMock()
    result = process_tools(None, [(tool, input_value)])
    assert result[0] == expected


@pytest.mark.parametrize(
    "input_model,expected_dict",
    [
        (SimpleModel(name="test", value=1), {"name": "test", "value": 1}),
        (
            NestedModel(simple=SimpleModel(name="nested", value=2), values=[1, 2, 3]),
            {"simple": {"name": "nested", "value": 2}, "values": [1, 2, 3]},
        ),
    ],
)
def test_transform_tool_outputs_pydantic_models(
    process_tools: Any, input_model: BaseModel, expected_dict: dict
) -> None:
    tool = MagicMock()
    result = process_tools(None, [(tool, input_model)])
    assert json.loads(result[0]) == expected_dict


@pytest.mark.parametrize(
    "container_type,input_value,expected_type",
    [
        ("list", ["string", 42, SimpleModel(name="item", value=3)], list),
        (
            "tuple",
            ("string", 42, SimpleModel(name="item", value=3)),
            list,
        ),
    ],
)
def test_transform_tool_outputs_containers(
    process_tools: Any, container_type: str, input_value: Any, expected_type: type
) -> None:
    tool = MagicMock()
    result = process_tools(None, [(tool, input_value)])
    parsed = json.loads(result[0])
    assert isinstance(parsed, expected_type)
    assert parsed == ["string", 42, {"name": "item", "value": 3}]


def test_transform_tool_outputs_sets(process_tools: Any) -> None:
    tool = MagicMock()
    result = process_tools(None, [(tool, {"string", 42, 3.14})])
    parsed = json.loads(result[0])
    assert isinstance(parsed, list)
    assert set(parsed) == {"string", 42, 3.14}


def test_transform_tool_outputs_nested_dictionaries(process_tools: Any) -> None:
    """Tests the serialization of nested dictionaries."""

    class NestedModel(BaseModel):
        simple: SimpleModel
        values: list[int]

    tool = MagicMock()
    result = process_tools(
        None,
        [(tool, {"simple": SimpleModel(name="test", value=1), "values": [1, 2, 3]})],
    )
    parsed = json.loads(result[0])
    assert parsed == {"simple": {"name": "test", "value": 1}, "values": [1, 2, 3]}


def test_transform_tool_outputs_unsupported_type(process_tools: Any) -> None:
    """Tests the serialization of an unsupported type."""

    class UnsupportedType:
        pass

    tool = MagicMock()
    with pytest.raises(TypeError) as exc_info:
        process_tools(None, [(tool, UnsupportedType())])
    assert "Unsupported type for serialization" in str(exc_info.value)
