"""Tests for ToolSchema functionality."""

from typing import Annotated

import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel, Field, PydanticSchemaGenerationError

from mirascope import llm


def test_complex_tool_schema_snapshot() -> None:
    """Test comprehensive tool with complex types generates expected parameter schema."""

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

    schema = llm.tools.ToolSchema(complex_tool)

    assert schema.parameters.model_dump(by_alias=True, exclude_none=True) == snapshot(
        {
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
        }
    )


def test_strict_mode() -> None:
    """Test strict mode flag is properly set."""

    def simple_tool() -> str:
        """A simple tool."""
        raise NotImplementedError

    normal_schema = llm.tools.ToolSchema(simple_tool)
    strict_schema = llm.tools.ToolSchema(simple_tool, strict=True)

    assert normal_schema.strict is False
    assert strict_schema.strict is True


def test_default_description() -> None:
    """Test default description when no docstring provided."""

    def tool_no_docstring() -> str:
        raise NotImplementedError

    schema = llm.tools.ToolSchema(tool_no_docstring)
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

    schema = llm.tools.ToolSchema(tool_with_multiline_docstring)
    expected = "Long docstring.\n\nThis is a multiline docstring\nwith some indentation.\n\nIt should be cleaned up properly."
    assert schema.description == expected


def test_no_parameters() -> None:
    """Test tool with no parameters."""

    def no_param_tool() -> str:
        """A tool with no parameters."""
        raise NotImplementedError

    schema = llm.tools.ToolSchema(no_param_tool)

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

    instance_schema = llm.tools.ToolSchema(TestClass.instance_method)
    class_schema = llm.tools.ToolSchema(TestClass.class_method)

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

    schema = llm.tools.ToolSchema(tool_with_annotated_no_field)
    assert schema.parameters.model_dump(by_alias=True, exclude_none=True) == snapshot(
        {
            "properties": {"param": {"title": "Param", "type": "string"}},
            "required": ["param"],
            "additionalProperties": False,
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
        llm.tools.ToolSchema(tool_with_non_jsonable)


def test_google_style_docstring_parameter_descriptions() -> None:
    """Test parsing parameter descriptions from Google-style docstrings."""

    def google_style_tool(name: str, age: int, is_active: bool = True) -> str:
        """A tool with Google-style parameter documentation.

        Args:
            name: The person's name
            age (int): The person's age in years
            is_active: Whether the person is currently active

        Returns:
            A formatted string with the information
        """
        raise NotImplementedError

    schema = llm.tools.ToolSchema(google_style_tool)

    assert schema.parameters.model_dump(by_alias=True, exclude_none=True) == snapshot(
        {
            "properties": {
                "name": {
                    "description": "The person's name",
                    "title": "Name",
                    "type": "string",
                },
                "age": {
                    "description": "The person's age in years",
                    "title": "Age",
                    "type": "integer",
                },
                "is_active": {
                    "default": True,
                    "description": "Whether the person is currently active",
                    "title": "Is Active",
                    "type": "boolean",
                },
            },
            "required": ["name", "age"],
            "additionalProperties": False,
        }
    )


def test_field_annotation_overrides_docstring() -> None:
    """Test that Field annotation descriptions take precedence over docstring."""

    def tool_with_both_docstring_descr_and_annotation(
        param: Annotated[str, Field(description="Field description")],
    ) -> str:
        """A tool where Field annotation should override docstring.

        Args:
            param: Docstring description that should be ignored
        """
        raise NotImplementedError

    schema = llm.tools.ToolSchema(tool_with_both_docstring_descr_and_annotation)

    assert schema.parameters.properties["param"]["description"] == "Field description"


def test_no_docstring_no_descriptions() -> None:
    """Test that parameters without docstrings have no descriptions."""

    def no_docs_tool(param1: str, param2: int) -> str:
        raise NotImplementedError

    schema = llm.tools.ToolSchema(no_docs_tool)

    assert "description" not in schema.parameters.properties["param1"]
    assert "description" not in schema.parameters.properties["param2"]


def test_tool_schema_is_hashable() -> None:
    """Test that ToolSchema instances are hashable."""

    def sample_tool(param: str) -> str:
        """A sample tool."""
        raise NotImplementedError

    schema = llm.tools.ToolSchema(sample_tool)

    hash_value = hash(schema)
    assert isinstance(hash_value, int)

    schema_set = {schema}
    schema_dict = {schema: "value"}
    assert len(schema_set) == 1
    assert schema_dict[schema] == "value"


def test_equivalent_schemas_have_same_hash() -> None:
    """Test that equivalent ToolSchemas have the same hash."""

    def sample_function(param: str) -> str:
        """A sample function."""
        return param

    schema1 = llm.tools.ToolSchema(sample_function)
    schema2 = llm.tools.ToolSchema(sample_function)

    assert hash(schema1) == hash(schema2)

    schema_set = {schema1, schema2}
    assert len(schema_set) == 1


def test_different_schemas_have_different_hashes() -> None:
    """Test that different ToolSchemas have different hashes."""

    def func1(param: str) -> str:
        """First function."""
        return param

    def func2(param: int) -> str:
        """Second function."""
        return str(param)

    schema1 = llm.tools.ToolSchema(func1)
    schema2 = llm.tools.ToolSchema(func2)

    assert hash(schema1) != hash(schema2)


def test_schema_hash_consistent_across_calls() -> None:
    """Test that hash is consistent across multiple calls."""

    def sample_function(param: str) -> str:
        """A sample function."""
        return param

    schema = llm.tools.ToolSchema(sample_function)

    hash1 = hash(schema)
    hash2 = hash(schema)
    hash3 = hash(schema)

    assert hash1 == hash2 == hash3


def test_matches_matching_tool_call() -> None:
    """Test that matches returns True for ToolCall with same name."""

    def sample_tool(param: str) -> str:
        """A sample tool."""
        return param

    schema = llm.tools.ToolSchema(sample_tool)
    tool_call = llm.ToolCall(
        id="test_id", name="sample_tool", args='{"param": "value"}'
    )

    assert schema.can_execute(tool_call)


def test_matches_non_matching_tool_call() -> None:
    """Test that matches returns False for ToolCall with different name."""

    def sample_tool(param: str) -> str:
        """A sample tool."""
        return param

    schema = llm.tools.ToolSchema(sample_tool)
    tool_call = llm.ToolCall(
        id="test_id", name="different_tool", args='{"param": "value"}'
    )

    assert not schema.can_execute(tool_call)


def test_matches_ignores_args() -> None:
    """Test that matches only checks name, ignoring args."""

    def sample_tool(param: str) -> str:
        """A sample tool."""
        return param

    schema = llm.tools.ToolSchema(sample_tool)
    tool_call = llm.ToolCall(
        id="test_id", name="sample_tool", args='{"invalid": "json"}'
    )

    assert schema.can_execute(tool_call)


def test_cannot_use_reserved_names() -> None:
    """Test that matches only checks name, ignoring args."""

    def __mirascope_formatted_output_tool__(param: str) -> str:
        """A sample tool."""
        return param

    with pytest.raises(ValueError, match="reserved name"):
        llm.tools.ToolSchema(__mirascope_formatted_output_tool__)


def test_context_tool_equivalence() -> None:
    """Make non-context and context tool schemas equivalent."""

    def make_non_context() -> llm.tools.AnyToolSchema:
        @llm.tool
        def example(arg: str) -> str:
            return arg

        return example

    def make_context() -> llm.tools.AnyToolSchema:
        @llm.tool
        def example(ctx: llm.Context[None], arg: str) -> str:
            return arg

        return example

    non_context_schema = make_non_context()
    context_schema = make_context()

    assert non_context_schema.name == context_schema.name
    assert non_context_schema.description == context_schema.description
    assert non_context_schema.parameters == context_schema.parameters
    assert hash(non_context_schema) == hash(context_schema)
