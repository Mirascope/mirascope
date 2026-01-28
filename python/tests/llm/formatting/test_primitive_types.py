"""Tests for primitive type utilities."""

from enum import Enum
from typing import Annotated, Literal, Optional

import pytest
from pydantic import BaseModel, Field, ValidationError

from mirascope.llm.formatting.primitives import create_wrapper_model, is_primitive_type


class Book(BaseModel):
    """A book model for testing."""

    title: str
    author: str


class Color(Enum):
    """An enum for testing."""

    RED = "red"
    BLUE = "blue"
    GREEN = "green"


def test_is_primitive_type_basic_primitives() -> None:
    """Test detection of basic primitive types."""
    assert is_primitive_type(str) is True
    assert is_primitive_type(int) is True
    assert is_primitive_type(float) is True
    assert is_primitive_type(bool) is True
    assert is_primitive_type(bytes) is True
    assert is_primitive_type(list) is True
    assert is_primitive_type(dict) is True
    assert is_primitive_type(set) is True
    assert is_primitive_type(tuple) is True


def test_is_primitive_type_generics() -> None:
    """Test detection of generic types."""
    assert is_primitive_type(list[int]) is True
    assert is_primitive_type(list[Book]) is True
    assert is_primitive_type(dict[str, int]) is True
    assert is_primitive_type(dict[str, Book]) is True
    assert is_primitive_type(set[str]) is True
    assert is_primitive_type(tuple[int, str]) is True


def test_is_primitive_type_enum() -> None:
    """Test detection of Enum types."""
    assert is_primitive_type(Color) is True


def test_is_primitive_type_literal() -> None:
    """Test detection of Literal types."""
    assert is_primitive_type(Literal["a", "b"]) is True
    assert is_primitive_type(Literal[1, 2, 3]) is True
    assert is_primitive_type(Literal["option1"]) is True


def test_is_primitive_type_union() -> None:
    """Test detection of Union types."""
    assert is_primitive_type(str | int) is True
    assert is_primitive_type(str | None) is True
    assert is_primitive_type(Optional[str]) is True  # noqa: UP045 # noqa: UP007 (expect error for testing)
    assert is_primitive_type(int | str | float) is True


def test_is_primitive_type_annotated() -> None:
    """Test detection of Annotated types."""
    assert is_primitive_type(Annotated[str, "description"]) is True
    assert is_primitive_type(Annotated[int, Field(ge=0)]) is True
    assert is_primitive_type(Annotated[list[Book], Field(description="Books")]) is True


def test_is_primitive_type_base_model() -> None:
    """Test that BaseModel subclasses are NOT primitives."""
    assert is_primitive_type(Book) is False
    assert is_primitive_type(BaseModel) is False


def test_is_primitive_type_none() -> None:
    """Test that None is NOT a primitive."""
    assert is_primitive_type(None) is False
    assert is_primitive_type(type(None)) is False


def test_create_wrapper_model_str() -> None:
    """Test wrapper creation for str."""
    wrapper = create_wrapper_model(str)

    assert wrapper.__name__ == "strOutput"

    assert hasattr(wrapper, "model_fields")
    assert "output" in wrapper.model_fields

    instance = wrapper(output="hello")
    assert instance.output == "hello"

    schema = wrapper.model_json_schema()
    assert "properties" in schema
    assert "output" in schema["properties"]


def test_create_wrapper_model_int() -> None:
    """Test wrapper creation for int."""
    wrapper = create_wrapper_model(int)

    assert wrapper.__name__ == "intOutput"

    instance = wrapper(output=42)
    assert instance.output == 42
    assert isinstance(instance.output, int)


def test_create_wrapper_model_list() -> None:
    """Test wrapper creation for bare list."""
    wrapper = create_wrapper_model(list)

    assert "list" in wrapper.__name__.lower()

    instance = wrapper(output=[1, 2, 3])
    assert instance.output == [1, 2, 3]


def test_create_wrapper_model_list_of_ints() -> None:
    """Test wrapper creation for list[int]."""
    wrapper = create_wrapper_model(list[int])

    instance = wrapper(output=[1, 2, 3])
    assert instance.output == [1, 2, 3]
    assert all(isinstance(x, int) for x in instance.output)

    with pytest.raises(ValidationError):
        wrapper(output=["not", "ints"])


def test_create_wrapper_model_list_of_models() -> None:
    """Test wrapper creation for list[Book]."""
    wrapper = create_wrapper_model(list[Book])

    books_data = [
        {"title": "Book 1", "author": "Author 1"},
        {"title": "Book 2", "author": "Author 2"},
    ]
    instance = wrapper(output=books_data)
    assert len(instance.output) == 2
    assert instance.output[0].title == "Book 1"
    assert isinstance(instance.output[0], Book)

    schema = wrapper.model_json_schema()
    assert "$defs" in schema or "definitions" in schema


def test_create_wrapper_model_dict() -> None:
    """Test wrapper creation for dict[str, int]."""
    wrapper = create_wrapper_model(dict[str, int])

    instance = wrapper(output={"a": 1, "b": 2})
    assert instance.output == {"a": 1, "b": 2}

    with pytest.raises(ValidationError):
        wrapper(output={"a": "not an int"})


def test_create_wrapper_model_dict_with_model_values() -> None:
    """Test wrapper creation for dict[str, Book]."""
    wrapper = create_wrapper_model(dict[str, Book])

    books_data = {
        "book1": {"title": "Title 1", "author": "Author 1"},
        "book2": {"title": "Title 2", "author": "Author 2"},
    }
    instance = wrapper(output=books_data)
    assert len(instance.output) == 2
    assert instance.output["book1"].title == "Title 1"
    assert isinstance(instance.output["book1"], Book)


def test_create_wrapper_model_annotated() -> None:
    """Test wrapper creation for Annotated types."""
    annotated_type = Annotated[str, Field(description="A description", min_length=1)]
    wrapper = create_wrapper_model(annotated_type)

    assert "str" in wrapper.__name__

    instance = wrapper(output="test")
    assert instance.output == "test"

    with pytest.raises(ValidationError):
        wrapper(output="")


def test_create_wrapper_model_set() -> None:
    """Test wrapper creation for set."""
    wrapper = create_wrapper_model(set[str])

    instance = wrapper(output={"a", "b", "c"})
    assert instance.output == {"a", "b", "c"}
    assert isinstance(instance.output, set)


def test_create_wrapper_model_tuple() -> None:
    """Test wrapper creation for tuple."""
    wrapper = create_wrapper_model(tuple[int, str])

    instance = wrapper(output=(1, "test"))
    assert instance.output == (1, "test")
    assert isinstance(instance.output, tuple)


def test_create_wrapper_model_union() -> None:
    """Test wrapper creation for Union types."""
    wrapper = create_wrapper_model(str | int)

    instance1 = wrapper(output="string")
    assert instance1.output == "string"

    instance2 = wrapper(output=42)
    assert instance2.output == 42


def test_create_wrapper_model_optional() -> None:
    """Test wrapper creation for Optional types."""
    wrapper = create_wrapper_model(str | None)

    instance1 = wrapper(output="value")
    assert instance1.output == "value"

    instance2 = wrapper(output=None)
    assert instance2.output is None


def test_create_wrapper_model_literal() -> None:
    """Test wrapper creation for Literal types."""
    wrapper = create_wrapper_model(Literal["a", "b", "c"])

    instance = wrapper(output="a")
    assert instance.output == "a"

    with pytest.raises(ValidationError):
        wrapper(output="d")


def test_create_wrapper_model_enum() -> None:
    """Test wrapper creation for Enum types."""
    wrapper = create_wrapper_model(Color)

    instance = wrapper(output="red")
    assert instance.output == Color.RED

    instance2 = wrapper(output=Color.BLUE)
    assert instance2.output == Color.BLUE


def test_create_wrapper_model_bytes() -> None:
    """Test wrapper creation for bytes."""
    wrapper = create_wrapper_model(bytes)

    instance = wrapper(output=b"hello")
    assert instance.output == b"hello"
    assert isinstance(instance.output, bytes)


def test_create_wrapper_model_nested_generics() -> None:
    """Test wrapper creation for nested generic types."""
    wrapper = create_wrapper_model(dict[str, list[int]])

    data = {"nums1": [1, 2, 3], "nums2": [4, 5, 6]}
    instance = wrapper(output=data)
    assert instance.output == data
    assert isinstance(instance.output["nums1"], list)


def test_create_wrapper_model_json_validation() -> None:
    """Test that wrapper model validates JSON correctly."""
    wrapper = create_wrapper_model(list[Book])

    json_str = '{"output": [{"title": "Book", "author": "Author"}]}'
    instance = wrapper.model_validate_json(json_str)
    assert len(instance.output) == 1
    assert instance.output[0].title == "Book"

    invalid_json = '[{"title": "Book", "author": "Author"}]'
    with pytest.raises(ValidationError):
        wrapper.model_validate_json(invalid_json)
