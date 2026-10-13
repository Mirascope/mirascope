"""Tests for the type_model module."""

import json
from typing import Any

from api2mdx.type_model import (
    EnumEncoder,
    GenericType,
    ParameterInfo,
    ReturnInfo,
    SimpleType,
    TypeKind,
)


def assert_json_equal(actual: Any, expected: Any) -> None:  # noqa: ANN401
    """Assert that two objects are equal when serialized to JSON."""
    actual_json = json.loads(actual.to_json())
    expected_json = json.loads(expected.to_json())
    assert actual_json == expected_json, (
        f"JSON not equal: {json.dumps(actual_json, cls=EnumEncoder)} != {json.dumps(expected_json, cls=EnumEncoder)}"
    )


def test_type_model_classes() -> None:
    """Test the type model classes."""
    # Test simple type
    simple_type = SimpleType(type_str="str")
    assert simple_type.type_str == "str"
    assert simple_type.kind == TypeKind.SIMPLE
    assert simple_type.description is None

    # Test simple type with description
    simple_type_with_desc = SimpleType(type_str="int", description="A whole number")
    assert simple_type_with_desc.type_str == "int"
    assert simple_type_with_desc.kind == TypeKind.SIMPLE
    assert simple_type_with_desc.description == "A whole number"

    # Test generic type
    generic_type = GenericType(
        type_str="List[str]",
        base_type=SimpleType(type_str="List"),
        parameters=[SimpleType(type_str="str")],
    )
    assert generic_type.type_str == "List[str]"
    assert generic_type.kind == TypeKind.GENERIC
    assert generic_type.description is None
    assert isinstance(generic_type.base_type, SimpleType)
    assert generic_type.base_type.type_str == "List"
    assert len(generic_type.parameters) == 1
    assert isinstance(generic_type.parameters[0], SimpleType)
    assert generic_type.parameters[0].type_str == "str"

    # Test generic type with different kind
    union_type = GenericType(
        type_str="str | int",
        base_type=SimpleType(type_str="Union"),
        parameters=[SimpleType(type_str="str"), SimpleType(type_str="int")],
        kind=TypeKind.UNION,
    )
    assert union_type.type_str == "str | int"
    assert union_type.kind == TypeKind.UNION
    assert isinstance(union_type.base_type, SimpleType)
    assert union_type.base_type.type_str == "Union"
    assert len(union_type.parameters) == 2


def test_json_serialization() -> None:
    """Test JSON serialization of type models."""
    # Test simple type
    type_info = SimpleType(type_str="str")

    # Serialize and deserialize
    json_str = type_info.to_json()
    parsed = json.loads(json_str)

    # Check fields are preserved
    assert parsed["type_str"] == "str"
    assert parsed["kind"] == "simple"
    assert parsed["description"] is None
    assert parsed["symbol_name"] is None
    assert parsed["doc_url"] is None

    # Test generic type with nested structure
    nested_type = GenericType(
        type_str="List[Dict[str, int]]",
        base_type=SimpleType(type_str="List"),
        parameters=[
            GenericType(
                type_str="Dict[str, int]",
                base_type=SimpleType(type_str="Dict"),
                parameters=[SimpleType(type_str="str"), SimpleType(type_str="int")],
            )
        ],
    )

    # Verify the JSON structure
    expected_json_snapshot = {
        "kind": "generic",
        "type_str": "List[Dict[str, int]]",
        "description": None,
        "base_type": {
            "kind": "simple",
            "type_str": "List",
            "description": None,
            "symbol_name": None,
            "doc_url": None,
        },
        "parameters": [
            {
                "kind": "generic",
                "type_str": "Dict[str, int]",
                "description": None,
                "base_type": {
                    "kind": "simple",
                    "type_str": "Dict",
                    "description": None,
                    "symbol_name": None,
                    "doc_url": None,
                },
                "parameters": [
                    {
                        "kind": "simple",
                        "type_str": "str",
                        "description": None,
                        "symbol_name": None,
                        "doc_url": None,
                    },
                    {
                        "kind": "simple",
                        "type_str": "int",
                        "description": None,
                        "symbol_name": None,
                        "doc_url": None,
                    },
                ],
                "doc_url": None,
            }
        ],
        "doc_url": None,
    }

    # Verify the exact JSON structure matches our expectation
    actual_json = json.loads(nested_type.to_json())
    assert actual_json == expected_json_snapshot, (
        "JSON snapshot does not match expected format"
    )

    # Test enum serialization
    enum_value = TypeKind.UNION
    json_str = json.dumps(enum_value, cls=EnumEncoder)
    assert json_str == '"union"'


def test_parameter_info() -> None:
    """Test the ParameterInfo class."""
    # Create a simple parameter
    param = ParameterInfo(
        name="count",
        type_info=SimpleType(type_str="int"),
        description="Number of items to return",
    )

    assert param.name == "count"
    assert isinstance(param.type_info, SimpleType)
    assert param.type_info.type_str == "int"
    assert param.description == "Number of items to return"
    assert param.default is None
    assert param.is_optional is False

    # Create a parameter with default value
    param_with_default = ParameterInfo(
        name="limit",
        type_info=SimpleType(type_str="int"),
        description="Maximum number of results",
        default="100",
        is_optional=True,
    )

    assert param_with_default.name == "limit"
    assert param_with_default.default == "100"
    assert param_with_default.is_optional is True

    # Test JSON serialization
    param_json = json.loads(param.to_json())
    assert param_json["name"] == "count"
    assert param_json["type_info"]["type_str"] == "int"
    assert param_json["type_info"]["kind"] == "simple"
    assert param_json["description"] == "Number of items to return"
    assert param_json["default"] is None
    assert param_json["is_optional"] is False

    # Create a parameter with complex type
    complex_param = ParameterInfo(
        name="items",
        type_info=GenericType(
            type_str="List[Dict[str, int]]",
            base_type=SimpleType(type_str="List"),
            parameters=[
                GenericType(
                    type_str="Dict[str, int]",
                    base_type=SimpleType(type_str="Dict"),
                    parameters=[
                        SimpleType(type_str="str"),
                        SimpleType(type_str="int"),
                    ],
                )
            ],
        ),
    )

    # Test complex type in parameter
    complex_json = json.loads(complex_param.to_json())
    assert complex_json["name"] == "items"
    assert complex_json["type_info"]["type_str"] == "List[Dict[str, int]]"
    assert complex_json["type_info"]["base_type"]["type_str"] == "List"
    assert len(complex_json["type_info"]["parameters"]) == 1
    assert complex_json["type_info"]["parameters"][0]["type_str"] == "Dict[str, int]"


def test_return_info() -> None:
    """Test the ReturnInfo class."""
    # Create a simple return info
    ret = ReturnInfo(
        type_info=SimpleType(type_str="bool"),
        description="Whether the operation succeeded",
    )

    assert isinstance(ret.type_info, SimpleType)
    assert ret.type_info.type_str == "bool"
    assert ret.description == "Whether the operation succeeded"
    assert ret.name is None

    # Create a return info with a name
    named_ret = ReturnInfo(
        type_info=SimpleType(type_str="str"),
        description="The generated ID",
        name="id",
    )

    assert named_ret.type_info.type_str == "str"
    assert named_ret.name == "id"

    # Test JSON serialization
    ret_json = json.loads(ret.to_json())
    assert ret_json["type_info"]["type_str"] == "bool"
    assert ret_json["type_info"]["kind"] == "simple"
    assert ret_json["description"] == "Whether the operation succeeded"
    assert ret_json["name"] is None

    # Create a return info with complex type
    complex_ret = ReturnInfo(
        type_info=GenericType(
            type_str="Dict[str, List[int]]",
            base_type=SimpleType(type_str="Dict"),
            parameters=[
                SimpleType(type_str="str"),
                GenericType(
                    type_str="List[int]",
                    base_type=SimpleType(type_str="List"),
                    parameters=[SimpleType(type_str="int")],
                ),
            ],
        ),
    )

    # Test complex type in return info
    complex_json = json.loads(complex_ret.to_json())
    assert complex_json["type_info"]["type_str"] == "Dict[str, List[int]]"
    assert complex_json["type_info"]["base_type"]["type_str"] == "Dict"
    assert len(complex_json["type_info"]["parameters"]) == 2
    assert complex_json["type_info"]["parameters"][1]["type_str"] == "List[int]"
