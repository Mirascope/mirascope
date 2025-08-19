"""Tests for the @format decorator."""

from typing import Annotated, cast

import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel, Field

from mirascope import llm


def get_format(x: type[llm.formatting.FormatT]) -> llm.Format:
    assert hasattr(x, "__response_format__")
    format = cast(llm.formatting.Formattable, x).__response_format__
    assert isinstance(format, llm.formatting.Format)
    return format


def test_format_decorator_basic() -> None:
    """Test basic format decorator functionality."""

    @llm.format
    class Book(BaseModel):
        title: str
        author: str

    format_obj = get_format(Book)
    assert format_obj.name == "Book"
    assert format_obj.description is None
    assert format_obj.mode == "strict-or-tool"
    assert format_obj.formatting_instructions is None


@pytest.mark.parametrize(
    "mode", ["strict", "json", "tool", "strict-or-tool", "strict-or-json"]
)
def test_format_decorator_all_modes(mode: llm.formatting.FormattingMode) -> None:
    """Test format decorator with all supported modes."""

    @llm.format(mode=mode)
    class ModeTest(BaseModel):
        content: str

    format_obj = get_format(ModeTest)
    assert format_obj.name == "ModeTest"
    assert format_obj.description is None
    assert format_obj.mode == mode
    assert format_obj.formatting_instructions is None


def test_format_decorator_schema_snapshot() -> None:
    """Test that format decorator generates correct schema."""

    @llm.format()
    class ComplexModel(BaseModel):
        """A complex model for testing schema generation."""

        id: int
        name: str
        description: Annotated[str, Field(description="A detailed description")]
        tags: list[str] = []
        metadata: dict[str, str] = {}
        is_active: bool = True

    format_obj = get_format(ComplexModel)
    assert format_obj.name == "ComplexModel"
    assert format_obj.description == "A complex model for testing schema generation."

    schema = format_obj.schema
    assert schema == snapshot(
        {
            "type": "object",
            "properties": {
                "id": {"title": "Id", "type": "integer"},
                "name": {"title": "Name", "type": "string"},
                "description": {
                    "description": "A detailed description",
                    "title": "Description",
                    "type": "string",
                },
                "tags": {
                    "default": [],
                    "items": {"type": "string"},
                    "title": "Tags",
                    "type": "array",
                },
                "metadata": {
                    "additionalProperties": {"type": "string"},
                    "default": {},
                    "title": "Metadata",
                    "type": "object",
                },
                "is_active": {"default": True, "title": "Is Active", "type": "boolean"},
            },
            "required": ["id", "name", "description"],
            "title": "ComplexModel",
            "description": "A complex model for testing schema generation.",
        }
    )


def test_format_decorator_with_formatting_instructions() -> None:
    """Test format decorator with formatting instructions."""

    @llm.format()
    class TaskWithInstructions(BaseModel):
        task: str
        priority: int

        @classmethod
        def formatting_instructions(cls) -> str:
            return """
            Always use clear, concise language for tasks.
            Also, be sure not to include extra newlines.
            """

    format_obj = get_format(TaskWithInstructions)
    assert (
        format_obj.formatting_instructions
        == "Always use clear, concise language for tasks.\nAlso, be sure not to include extra newlines."
    )


def test_format_decorator_factory_vs_direct() -> None:
    """Test that factory and direct application produce equivalent results."""

    def direct_decorated() -> type[BaseModel]:
        @llm.format
        class Example(BaseModel):
            text: str

        return Example

    def factory_decorated() -> type[BaseModel]:
        @llm.format()
        class Example(BaseModel):
            text: str

        return Example

    assert get_format(direct_decorated()) == get_format(factory_decorated())


def test_format_decorator_preserves_class_functionality() -> None:
    """Test that format decorator doesn't break normal class usage."""

    @llm.format()
    class User(BaseModel):
        name: str
        age: int

        def greet(self) -> str:
            return f"Hello, I'm {self.name}"

    user = User(name="Alice", age=30)
    assert user.name == "Alice"
    assert user.age == 30
    assert user.greet() == "Hello, I'm Alice"


def test_format_decorator_nested_models() -> None:
    """Test format decorator with nested Pydantic models."""

    class Address(BaseModel):
        street: str
        city: str

    @llm.format()
    class Person(BaseModel):
        name: str
        address: Address

    schema = get_format(Person).schema
    assert schema == snapshot(
        {
            "$defs": {
                "Address": {
                    "properties": {
                        "street": {"title": "Street", "type": "string"},
                        "city": {"title": "City", "type": "string"},
                    },
                    "required": ["street", "city"],
                    "title": "Address",
                    "type": "object",
                }
            },
            "properties": {
                "name": {"title": "Name", "type": "string"},
                "address": {"$ref": "#/$defs/Address"},
            },
            "required": ["name", "address"],
            "title": "Person",
            "type": "object",
        }
    )


def test_format_decorator_name_and_description() -> None:
    """Test that format decorator correctly extracts name and description."""

    @llm.format()
    class BookWithDescription(BaseModel):
        """A comprehensive book record for library management.

        This model stores essential information about books
        including metadata and availability status.
        """

        title: str
        author: str
        isbn: str

    format_obj = get_format(BookWithDescription)
    assert format_obj.name == "BookWithDescription"
    expected_description = (
        "A comprehensive book record for library management.\n\n"
        "This model stores essential information about books\n"
        "including metadata and availability status."
    )
    assert format_obj.description == expected_description
