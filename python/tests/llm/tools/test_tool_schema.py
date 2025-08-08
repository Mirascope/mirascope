"""Tests for ToolSchema functionality."""

from typing import Annotated

import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel, Field, PydanticSchemaGenerationError

from mirascope import llm


def test_complex_tool_schema_snapshot() -> None:
    """Test comprehensive tool with complex types generates expected schema."""

    class ExampleModel(BaseModel):
        """An example model for testing."""

        id: int
        name: str
        tags: list[str] = []

    def complex_tool(
        basic_param: str,
        annotated_param: Annotated[
            int, Field(description="An annotated integer parameter")
        ],
        model_param: ExampleModel,
        optional_param: str = "default",
        union_param: str | int = "default_union",
    ) -> str:
        """A comprehensive tool for testing schema generation.

        This tool exercises various parameter types to ensure our schema
        generation handles complex cases correctly.
        """
        raise NotImplementedError

    schema = llm.tools.ToolSchema.from_function(complex_tool)

    assert schema.model_dump(by_alias=True, exclude_none=True) == snapshot(
        {
            "name": "complex_tool",
            "description": "A comprehensive tool for testing schema generation.\n\nThis tool exercises various parameter types to ensure our schema\ngeneration handles complex cases correctly.",
            "parameters": {
                "properties": {
                    "basic_param": {"title": "Basic Param", "type": "string"},
                    "annotated_param": {
                        "description": "An annotated integer parameter",
                        "title": "Annotated Param",
                        "type": "integer",
                    },
                    "model_param": {"$ref": "#/$defs/ExampleModel"},
                    "optional_param": {
                        "default": "default",
                        "title": "Optional Param",
                        "type": "string",
                    },
                    "union_param": {
                        "anyOf": [{"type": "string"}, {"type": "integer"}],
                        "default": "default_union",
                        "title": "Union Param",
                    },
                },
                "required": ["basic_param", "annotated_param", "model_param"],
                "additionalProperties": False,
                "$defs": {
                    "ExampleModel": {
                        "description": "An example model for testing.",
                        "properties": {
                            "id": {"title": "Id", "type": "integer"},
                            "name": {"title": "Name", "type": "string"},
                            "tags": {
                                "default": [],
                                "items": {"type": "string"},
                                "title": "Tags",
                                "type": "array",
                            },
                        },
                        "required": ["id", "name"],
                        "title": "ExampleModel",
                        "type": "object",
                    }
                },
            },
            "strict": False,
        }
    )


def test_strict_mode() -> None:
    """Test strict mode flag is properly set."""

    def simple_tool() -> str:
        """A simple tool."""
        raise NotImplementedError

    normal_schema = llm.tools.ToolSchema.from_function(simple_tool)
    strict_schema = llm.tools.ToolSchema.from_function(simple_tool, strict=True)

    assert normal_schema.strict is False
    assert strict_schema.strict is True


def test_default_description() -> None:
    """Test default description when no docstring provided."""

    def tool_no_docstring() -> str:
        raise NotImplementedError

    schema = llm.tools.ToolSchema.from_function(tool_no_docstring)
    assert schema.description == "tool_no_docstring"


def test_docstring_cleaning() -> None:
    """Test docstring indentation is properly cleaned."""

    def tool_with_multiline_docstring() -> str:
        """Long docstring.

        This is a multiline docstring
        with some indentation.

        It should be cleaned up properly.
        """
        raise NotImplementedError

    schema = llm.tools.ToolSchema.from_function(tool_with_multiline_docstring)
    expected = "Long docstring.\n\nThis is a multiline docstring\nwith some indentation.\n\nIt should be cleaned up properly."
    assert schema.description == expected


def test_no_parameters() -> None:
    """Test tool with no parameters."""

    def no_param_tool() -> str:
        """A tool with no parameters."""
        raise NotImplementedError

    schema = llm.tools.ToolSchema.from_function(no_param_tool)

    assert schema.parameters.properties == {}
    assert schema.parameters.required == []


def test_self_cls_parameters_skipped() -> None:
    """Test that self and cls parameters are properly ignored."""

    class TestClass:
        def instance_method(self, param: str) -> str:
            """Instance method."""
            raise NotImplementedError

        @classmethod
        def class_method(cls, param: int) -> str:
            """Class method."""
            raise NotImplementedError

    instance_schema = llm.tools.ToolSchema.from_function(TestClass.instance_method)
    class_schema = llm.tools.ToolSchema.from_function(TestClass.class_method)

    # Only the actual parameters should be present
    assert list(instance_schema.parameters.properties.keys()) == ["param"]
    assert list(class_schema.parameters.properties.keys()) == ["param"]

    assert instance_schema.parameters.required == ["param"]
    assert class_schema.parameters.required == ["param"]


def test_annotated_without_field_info() -> None:
    """Test that Annotated types without FieldInfo use core type and default."""

    def tool_with_annotated_no_field(
        param: Annotated[str, "some non-field annotation"],
    ) -> str:
        """Tool with Annotated type but no Field annotation."""
        raise NotImplementedError

    schema = llm.tools.ToolSchema.from_function(tool_with_annotated_no_field)
    assert schema.model_dump(by_alias=True, exclude_none=True) == snapshot(
        {
            "name": "tool_with_annotated_no_field",
            "description": "Tool with Annotated type but no Field annotation.",
            "parameters": {
                "properties": {"param": {"title": "Param", "type": "string"}},
                "required": ["param"],
                "additionalProperties": False,
            },
            "strict": False,
        }
    )


def test_non_jsonable_parameter_raises_error() -> None:
    """Test that non-jsonable parameter types raise schema generation error."""

    class NonJsonableClass:
        """A class that cannot be serialized to JSON."""

        pass

    def tool_with_non_jsonable(param: NonJsonableClass) -> str:
        """Tool with unsupported parameter type."""
        raise NotImplementedError

    with pytest.raises(PydanticSchemaGenerationError):
        llm.tools.ToolSchema.from_function(tool_with_non_jsonable)
