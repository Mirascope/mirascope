"""Tests for the parser module."""

import json
from typing import Any

import pytest

from api2mdx.parser import ParseError, parse_type_string
from api2mdx.type_model import EnumEncoder, GenericType, SimpleType, TypeKind


def assert_json_equal(actual: Any, expected: Any) -> None:  # noqa: ANN401
    """Assert that two objects are equal when serialized to JSON.

    Note: This ignores the doc_url field which may be set by the parser.
    """
    actual_json = json.loads(actual.to_json())
    expected_json = json.loads(expected.to_json())

    # Recursively remove doc_url and symbol_name from both objects for comparison
    def remove_doc_url(obj: Any) -> None:  # noqa: ANN401
        if isinstance(obj, dict):
            if "doc_url" in obj:
                obj.pop("doc_url")
            if "symbol_name" in obj:
                obj.pop("symbol_name")
            for value in list(obj.values()):
                remove_doc_url(value)
        elif isinstance(obj, list):
            for item in obj:
                remove_doc_url(item)

    remove_doc_url(actual_json)
    remove_doc_url(expected_json)

    assert actual_json == expected_json, (
        f"JSON not equal: {json.dumps(actual_json, cls=EnumEncoder)} != {json.dumps(expected_json, cls=EnumEncoder)}"
    )


def test_parse_simple_types() -> None:
    """Test parsing simple types."""
    # Test builtin types
    for type_str in ["str", "int", "float", "bool", "None"]:
        actual = parse_type_string(type_str)
        expected = SimpleType(type_str=type_str, kind=TypeKind.SIMPLE)
        assert_json_equal(actual, expected)

    # Test custom type
    custom_type = "MyCustomType"
    actual = parse_type_string(custom_type)
    expected = SimpleType(type_str=custom_type, kind=TypeKind.SIMPLE)
    assert_json_equal(actual, expected)

    # Test fully qualified type
    qualified_type = "mirascope.core.base.Response"
    actual = parse_type_string(qualified_type)
    expected = SimpleType(type_str=qualified_type, kind=TypeKind.SIMPLE)
    assert_json_equal(actual, expected)


def test_parse_generic_types() -> None:
    """Test parsing generic types."""
    # Test simple generic type
    type_str = "List[str]"
    actual = parse_type_string(type_str)
    expected = GenericType(
        type_str=type_str,
        base_type=SimpleType(type_str="List", kind=TypeKind.SIMPLE),
        parameters=[SimpleType(type_str="str", kind=TypeKind.SIMPLE)],
        kind=TypeKind.GENERIC,
    )
    assert_json_equal(actual, expected)

    # Test generic type with multiple parameters
    type_str = "Dict[str, int]"
    actual = parse_type_string(type_str)
    expected = GenericType(
        type_str=type_str,
        base_type=SimpleType(type_str="Dict", kind=TypeKind.SIMPLE),
        parameters=[
            SimpleType(type_str="str", kind=TypeKind.SIMPLE),
            SimpleType(type_str="int", kind=TypeKind.SIMPLE),
        ],
        kind=TypeKind.GENERIC,
    )
    assert_json_equal(actual, expected)

    # Test nested generic types
    type_str = "List[Dict[str, int]]"
    actual = parse_type_string(type_str)
    expected = GenericType(
        type_str=type_str,
        base_type=SimpleType(type_str="List", kind=TypeKind.SIMPLE),
        parameters=[
            GenericType(
                type_str="Dict[str, int]",
                base_type=SimpleType(type_str="Dict", kind=TypeKind.SIMPLE),
                parameters=[
                    SimpleType(type_str="str", kind=TypeKind.SIMPLE),
                    SimpleType(type_str="int", kind=TypeKind.SIMPLE),
                ],
                kind=TypeKind.GENERIC,
            )
        ],
        kind=TypeKind.GENERIC,
    )
    assert_json_equal(actual, expected)


def test_parse_union_types() -> None:
    """Test parsing union types."""
    # Test simple union (pipe syntax)
    type_str = "str | int"
    actual = parse_type_string(type_str)
    expected = GenericType(
        type_str=type_str,
        base_type=SimpleType(type_str="Union", kind=TypeKind.SIMPLE),
        parameters=[
            SimpleType(type_str="str", kind=TypeKind.SIMPLE),
            SimpleType(type_str="int", kind=TypeKind.SIMPLE),
        ],
        kind=TypeKind.UNION,
    )
    assert_json_equal(actual, expected)

    # Test union with more than two types
    type_str = "str | int | float | bool"
    actual = parse_type_string(type_str)
    expected = GenericType(
        type_str=type_str,
        base_type=SimpleType(type_str="Union", kind=TypeKind.SIMPLE),
        parameters=[
            SimpleType(type_str="str", kind=TypeKind.SIMPLE),
            SimpleType(type_str="int", kind=TypeKind.SIMPLE),
            SimpleType(type_str="float", kind=TypeKind.SIMPLE),
            SimpleType(type_str="bool", kind=TypeKind.SIMPLE),
        ],
        kind=TypeKind.UNION,
    )
    assert_json_equal(actual, expected)

    # Test Union[] syntax
    type_str = "Union[str, int]"
    actual = parse_type_string(type_str)
    expected = GenericType(
        type_str=type_str,
        base_type=SimpleType(type_str="Union", kind=TypeKind.SIMPLE),
        parameters=[
            SimpleType(type_str="str", kind=TypeKind.SIMPLE),
            SimpleType(type_str="int", kind=TypeKind.SIMPLE),
        ],
        kind=TypeKind.UNION,
    )
    assert_json_equal(actual, expected)

    # Test Optional[] syntax
    type_str = "Optional[str]"
    actual = parse_type_string(type_str)
    expected = GenericType(
        type_str=type_str,
        base_type=SimpleType(type_str="Optional", kind=TypeKind.SIMPLE),
        parameters=[SimpleType(type_str="str", kind=TypeKind.SIMPLE)],
        kind=TypeKind.OPTIONAL,  # Optional now has its own kind
    )
    assert_json_equal(actual, expected)


def test_parse_nested_union_types() -> None:
    """Test parsing nested union types."""
    # Test union with generic type
    type_str = "str | List[int]"
    actual = parse_type_string(type_str)
    expected = GenericType(
        type_str=type_str,
        base_type=SimpleType(type_str="Union", kind=TypeKind.SIMPLE),
        parameters=[
            SimpleType(type_str="str", kind=TypeKind.SIMPLE),
            GenericType(
                type_str="List[int]",
                base_type=SimpleType(type_str="List", kind=TypeKind.SIMPLE),
                parameters=[SimpleType(type_str="int", kind=TypeKind.SIMPLE)],
                kind=TypeKind.GENERIC,
            ),
        ],
        kind=TypeKind.UNION,
    )
    assert_json_equal(actual, expected)

    # Test union nested in generic
    type_str = "List[str | int]"
    actual = parse_type_string(type_str)
    expected = GenericType(
        type_str=type_str,
        base_type=SimpleType(type_str="List", kind=TypeKind.SIMPLE),
        parameters=[
            GenericType(
                type_str="str | int",
                base_type=SimpleType(type_str="Union", kind=TypeKind.SIMPLE),
                parameters=[
                    SimpleType(type_str="str", kind=TypeKind.SIMPLE),
                    SimpleType(type_str="int", kind=TypeKind.SIMPLE),
                ],
                kind=TypeKind.UNION,
            ),
        ],
        kind=TypeKind.GENERIC,
    )
    assert_json_equal(actual, expected)

    # Test complex nested union case
    type_str = "Dict[str | int, List[bool | float]]"
    actual = parse_type_string(type_str)
    expected = GenericType(
        type_str=type_str,
        base_type=SimpleType(type_str="Dict", kind=TypeKind.SIMPLE),
        parameters=[
            GenericType(
                type_str="str | int",
                base_type=SimpleType(type_str="Union", kind=TypeKind.SIMPLE),
                parameters=[
                    SimpleType(type_str="str", kind=TypeKind.SIMPLE),
                    SimpleType(type_str="int", kind=TypeKind.SIMPLE),
                ],
                kind=TypeKind.UNION,
            ),
            GenericType(
                type_str="List[bool | float]",
                base_type=SimpleType(type_str="List", kind=TypeKind.SIMPLE),
                parameters=[
                    GenericType(
                        type_str="bool | float",
                        base_type=SimpleType(type_str="Union", kind=TypeKind.SIMPLE),
                        parameters=[
                            SimpleType(type_str="bool", kind=TypeKind.SIMPLE),
                            SimpleType(type_str="float", kind=TypeKind.SIMPLE),
                        ],
                        kind=TypeKind.UNION,
                    ),
                ],
                kind=TypeKind.GENERIC,
            ),
        ],
        kind=TypeKind.GENERIC,
    )
    assert_json_equal(actual, expected)


def test_parse_tuple_types() -> None:
    """Test parsing tuple types."""
    # Test tuple with Tuple[] syntax
    type_str = "Tuple[str, int]"
    actual = parse_type_string(type_str)
    expected = GenericType(
        type_str=type_str,
        base_type=SimpleType(type_str="Tuple", kind=TypeKind.SIMPLE),
        parameters=[
            SimpleType(type_str="str", kind=TypeKind.SIMPLE),
            SimpleType(type_str="int", kind=TypeKind.SIMPLE),
        ],
        kind=TypeKind.TUPLE,
    )
    assert_json_equal(actual, expected)

    # Test tuple with [] syntax
    type_str = "[str, int]"
    actual = parse_type_string(type_str)
    expected = GenericType(
        type_str=type_str,
        base_type=SimpleType(type_str="tuple", kind=TypeKind.SIMPLE),
        parameters=[
            SimpleType(type_str="str", kind=TypeKind.SIMPLE),
            SimpleType(type_str="int", kind=TypeKind.SIMPLE),
        ],
        kind=TypeKind.TUPLE,
    )
    assert_json_equal(actual, expected)

    # Test nested tuple
    type_str = "Tuple[str, Tuple[int, bool]]"
    actual = parse_type_string(type_str)
    expected = GenericType(
        type_str=type_str,
        base_type=SimpleType(type_str="Tuple", kind=TypeKind.SIMPLE),
        parameters=[
            SimpleType(type_str="str", kind=TypeKind.SIMPLE),
            GenericType(
                type_str="Tuple[int, bool]",
                base_type=SimpleType(type_str="Tuple", kind=TypeKind.SIMPLE),
                parameters=[
                    SimpleType(type_str="int", kind=TypeKind.SIMPLE),
                    SimpleType(type_str="bool", kind=TypeKind.SIMPLE),
                ],
                kind=TypeKind.TUPLE,
            ),
        ],
        kind=TypeKind.TUPLE,
    )
    assert_json_equal(actual, expected)

    # Test nested bare tuple
    type_str = "[str, [int, bool]]"
    actual = parse_type_string(type_str)
    expected = GenericType(
        type_str=type_str,
        base_type=SimpleType(type_str="tuple", kind=TypeKind.SIMPLE),
        parameters=[
            SimpleType(type_str="str", kind=TypeKind.SIMPLE),
            GenericType(
                type_str="[int, bool]",
                base_type=SimpleType(type_str="tuple", kind=TypeKind.SIMPLE),
                parameters=[
                    SimpleType(type_str="int", kind=TypeKind.SIMPLE),
                    SimpleType(type_str="bool", kind=TypeKind.SIMPLE),
                ],
                kind=TypeKind.TUPLE,
            ),
        ],
        kind=TypeKind.TUPLE,
    )
    assert_json_equal(actual, expected)

    # Test mixed tuple nesting
    type_str = "Tuple[str, [int, bool]]"
    actual = parse_type_string(type_str)
    expected = GenericType(
        type_str=type_str,
        base_type=SimpleType(type_str="Tuple", kind=TypeKind.SIMPLE),
        parameters=[
            SimpleType(type_str="str", kind=TypeKind.SIMPLE),
            GenericType(
                type_str="[int, bool]",
                base_type=SimpleType(type_str="tuple", kind=TypeKind.SIMPLE),
                parameters=[
                    SimpleType(type_str="int", kind=TypeKind.SIMPLE),
                    SimpleType(type_str="bool", kind=TypeKind.SIMPLE),
                ],
                kind=TypeKind.TUPLE,
            ),
        ],
        kind=TypeKind.TUPLE,
    )
    assert_json_equal(actual, expected)


def test_parse_callable_types() -> None:
    """Test parsing callable types."""
    # Test basic callable
    type_str = "Callable[[str, int], bool]"
    actual = parse_type_string(type_str)
    expected = GenericType(
        type_str=type_str,
        base_type=SimpleType(type_str="Callable", kind=TypeKind.SIMPLE),
        parameters=[
            GenericType(
                type_str="[str, int]",
                base_type=SimpleType(type_str="tuple", kind=TypeKind.SIMPLE),
                parameters=[
                    SimpleType(type_str="str", kind=TypeKind.SIMPLE),
                    SimpleType(type_str="int", kind=TypeKind.SIMPLE),
                ],
                kind=TypeKind.TUPLE,
            ),
            SimpleType(type_str="bool", kind=TypeKind.SIMPLE),
        ],
        kind=TypeKind.CALLABLE,
    )
    assert_json_equal(actual, expected)

    # Test callable with empty arguments list (no parameters)
    type_str = "Callable[[], str]"
    actual = parse_type_string(type_str)
    expected = GenericType(
        type_str=type_str,
        base_type=SimpleType(type_str="Callable", kind=TypeKind.SIMPLE),
        parameters=[
            GenericType(
                type_str="[]",
                base_type=SimpleType(type_str="tuple", kind=TypeKind.SIMPLE),
                parameters=[],  # Empty parameters list
                kind=TypeKind.TUPLE,
            ),
            SimpleType(type_str="str", kind=TypeKind.SIMPLE),
        ],
        kind=TypeKind.CALLABLE,
    )
    assert_json_equal(actual, expected)

    # Test callable with complex return type
    type_str = "Callable[[str], Dict[str, int]]"
    actual = parse_type_string(type_str)
    expected = GenericType(
        type_str=type_str,
        base_type=SimpleType(type_str="Callable", kind=TypeKind.SIMPLE),
        parameters=[
            GenericType(
                type_str="[str]",
                base_type=SimpleType(type_str="tuple", kind=TypeKind.SIMPLE),
                parameters=[SimpleType(type_str="str", kind=TypeKind.SIMPLE)],
                kind=TypeKind.TUPLE,
            ),
            GenericType(
                type_str="Dict[str, int]",
                base_type=SimpleType(type_str="Dict", kind=TypeKind.SIMPLE),
                parameters=[
                    SimpleType(type_str="str", kind=TypeKind.SIMPLE),
                    SimpleType(type_str="int", kind=TypeKind.SIMPLE),
                ],
                kind=TypeKind.GENERIC,
            ),
        ],
        kind=TypeKind.CALLABLE,
    )
    assert_json_equal(actual, expected)

    # Test callable with union types
    type_str = "Callable[[str | int], bool | None]"
    actual = parse_type_string(type_str)
    expected = GenericType(
        type_str=type_str,
        base_type=SimpleType(type_str="Callable", kind=TypeKind.SIMPLE),
        parameters=[
            GenericType(
                type_str="[str | int]",
                base_type=SimpleType(type_str="tuple", kind=TypeKind.SIMPLE),
                parameters=[
                    GenericType(
                        type_str="str | int",
                        base_type=SimpleType(type_str="Union", kind=TypeKind.SIMPLE),
                        parameters=[
                            SimpleType(type_str="str", kind=TypeKind.SIMPLE),
                            SimpleType(type_str="int", kind=TypeKind.SIMPLE),
                        ],
                        kind=TypeKind.UNION,
                    ),
                ],
                kind=TypeKind.TUPLE,
            ),
            GenericType(
                type_str="bool | None",
                base_type=SimpleType(type_str="Union", kind=TypeKind.SIMPLE),
                parameters=[
                    SimpleType(type_str="bool", kind=TypeKind.SIMPLE),
                    SimpleType(type_str="None", kind=TypeKind.SIMPLE),
                ],
                kind=TypeKind.UNION,
            ),
        ],
        kind=TypeKind.CALLABLE,
    )
    assert_json_equal(actual, expected)


def test_error_handling() -> None:
    """Test error handling in the parser."""
    # Test unbalanced brackets
    with pytest.raises(ParseError):
        parse_type_string("List[str")

    # Test unexpected token - This will actually be caught by the unbalanced bracket check
    with pytest.raises(ParseError):
        parse_type_string("List[str]]")

    # Test invalid callable (wrong number of parameters)
    with pytest.raises(ParseError):
        parse_type_string("Callable[[str], bool, int]")

    # Test malformed type (balanced brackets but invalid syntax)
    with pytest.raises(ParseError):
        parse_type_string("List[,]")
