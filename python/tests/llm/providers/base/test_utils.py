"""Tests for base converter."""

from unittest.mock import patch

import pytest
from pydantic import BaseModel

from mirascope import llm
from mirascope.llm.providers.base import _utils


def test_encode_messages_with_system_first() -> None:
    """Test that system message is extracted when it's first."""
    messages = [
        llm.messages.system("You are a helpful assistant"),
        llm.messages.user("Hello"),
        llm.messages.assistant(
            "Hi there", model_id="openai/gpt-5", provider_id="openai"
        ),
        llm.messages.user("How are you?"),
    ]

    system_message, remaining_messages = _utils.extract_system_message(messages)

    assert system_message == "You are a helpful assistant"
    assert remaining_messages == messages[1:]


def test_encode_messages_no_system() -> None:
    """Test encoding messages when no system message is present."""
    messages = [
        llm.messages.user("Hello"),
        llm.messages.assistant(
            "Hi there", model_id="openai/gpt-5", provider_id="openai"
        ),
        llm.messages.user("How are you?"),
    ]
    system_message, remaining_messages = _utils.extract_system_message(messages)

    assert system_message is None
    assert remaining_messages == messages


def test_encode_messages_system_not_first_warns() -> None:
    """Test that system message not at index 0 is skipped with warning."""
    messages = [
        llm.messages.user("Hello"),
        llm.messages.system("You are a helpful assistant"),
        llm.messages.assistant(
            "Hi there", model_id="openai/gpt-5", provider_id="openai"
        ),
    ]

    with patch("logging.warning") as mock_warning:
        system_message, remaining_messages = _utils.extract_system_message(messages)

    assert system_message is None
    expected_remaining_messages = [messages[0], messages[2]]
    assert remaining_messages == expected_remaining_messages
    mock_warning.assert_called_once_with(
        "Skipping system message at index %d because it is not the first message",
        1,
    )


def test_encode_messages_multiple_system_warns() -> None:
    """Test that multiple system messages warn for non-first ones."""
    messages = [
        llm.messages.system("First system message"),
        llm.messages.user("Hello"),
        llm.messages.system("Second system message"),
        llm.messages.system("Third system message"),
    ]

    with patch("logging.warning") as mock_warning:
        system_message, remaining_messages = _utils.extract_system_message(messages)

    assert system_message == "First system message"
    expected_remaining_messages = [messages[1]]
    assert remaining_messages == expected_remaining_messages
    assert mock_warning.call_count == 2
    mock_warning.assert_any_call(
        "Skipping system message at index %d because it is not the first message",
        2,
    )
    mock_warning.assert_any_call(
        "Skipping system message at index %d because it is not the first message",
        3,
    )


def test_encode_messages_empty_list() -> None:
    """Test encoding an empty message list."""
    messages = []

    system_message, remaining_messages = _utils.extract_system_message(messages)

    assert system_message is None
    assert remaining_messages == []


def test_add_system_instructions_no_existing_system() -> None:
    """Test adding system instructions when no system message exists."""
    messages = [
        llm.messages.user("Hello"),
        llm.messages.assistant(
            "Hi there", model_id="openai/gpt-5", provider_id="openai"
        ),
    ]
    additional_instructions = "Be helpful and concise."

    result = _utils.add_system_instructions(messages, additional_instructions)

    expected = [
        llm.messages.system(additional_instructions),
        *messages,
    ]
    assert result == expected


def test_add_system_instructions_with_existing_system() -> None:
    """Test adding system instructions when system message already exists."""
    prior_system_message = "You are a helpful assistant."
    messages = [
        llm.messages.system(prior_system_message),
        llm.messages.user("Hello"),
        llm.messages.assistant(
            "Hi there", model_id="openai/gpt-5", provider_id="openai"
        ),
    ]
    additional_instructions = "Be helpful and concise."

    result = _utils.add_system_instructions(messages, additional_instructions)

    expected = [
        llm.messages.system(prior_system_message + "\n" + additional_instructions),
        *messages[1:],
    ]
    assert result == expected


def test_add_system_instructions_already_exists() -> None:
    """Test that duplicate instructions are not added."""
    additional_instructions = "Be helpful and concise."
    messages = [
        llm.messages.system(f"You are a helpful assistant.\n{additional_instructions}"),
        llm.messages.user("Hello"),
    ]

    result = _utils.add_system_instructions(messages, additional_instructions)

    assert result == messages


def test_add_system_instructions_empty_messages() -> None:
    """Test adding system instructions to empty message list."""
    messages = []
    additional_instructions = "Be helpful and concise."

    result = _utils.add_system_instructions(messages, additional_instructions)

    expected = [llm.messages.system(additional_instructions)]
    assert result == expected


def test_ensure_all_properties_required_basic() -> None:
    """Test that all properties are added to required array."""
    schema = {
        "type": "object",
        "properties": {
            "location": {"type": "string"},
            "unit": {"type": "string", "default": "fahrenheit"},
        },
        "required": ["location"],
    }

    _utils.ensure_all_properties_required(schema)

    assert set(schema["required"]) == {"location", "unit"}


def test_ensure_all_properties_required_nested() -> None:
    """Test that nested objects also have all properties required."""
    schema = {
        "type": "object",
        "properties": {
            "outer": {"type": "string"},
            "nested": {
                "type": "object",
                "properties": {
                    "inner1": {"type": "string"},
                    "inner2": {"type": "string", "default": "default_value"},
                },
                "required": ["inner1"],
            },
        },
        "required": ["outer"],
    }

    _utils.ensure_all_properties_required(schema)

    assert set(schema["required"]) == {"outer", "nested"}
    assert set(schema["properties"]["nested"]["required"]) == {"inner1", "inner2"}


def test_ensure_all_properties_required_with_defs() -> None:
    """Test that $defs are also processed."""
    schema = {
        "type": "object",
        "properties": {
            "item": {"$ref": "#/$defs/Item"},
        },
        "required": [],
        "$defs": {
            "Item": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "value": {"type": "integer", "default": 0},
                },
                "required": ["name"],
            }
        },
    }

    _utils.ensure_all_properties_required(schema)

    assert set(schema["required"]) == {"item"}
    assert set(schema["$defs"]["Item"]["required"]) == {"name", "value"}


def test_ensure_all_properties_required_in_list() -> None:
    """Test that objects within lists are processed."""
    schema = {
        "anyOf": [
            {
                "type": "object",
                "properties": {
                    "opt1": {"type": "string"},
                    "opt2": {"type": "string", "default": "default"},
                },
                "required": ["opt1"],
            },
            {"type": "null"},
        ]
    }

    _utils.ensure_all_properties_required(schema)

    assert set(schema["anyOf"][0]["required"]) == {"opt1", "opt2"}


def test_ensure_all_properties_required_empty_properties() -> None:
    """Test handling of object with empty properties."""
    schema = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    _utils.ensure_all_properties_required(schema)

    assert schema["required"] == []


def test_ensure_all_properties_required_no_properties_key() -> None:
    """Test handling of object without properties key."""
    schema = {"type": "object"}

    _utils.ensure_all_properties_required(schema)

    # Should not add a required key if there's no properties
    assert "required" not in schema


def test_has_strict_tools_with_empty_list() -> None:
    """Test that has_strict_tools returns False when tools is an empty list."""
    assert _utils.has_strict_tools([]) is False


class _DummyJsonable:
    def json(self) -> str:
        return '{"dummy": true}'


class _DummyModel(BaseModel):
    name: str
    count: int


def test_encode_tool_output_content_string() -> None:
    """Test that strings are returned as-is."""
    assert _utils.encode_tool_output_content("hello") == "hello"
    assert (
        _utils.encode_tool_output_content("Tool error: not found")
        == "Tool error: not found"
    )


def test_encode_tool_output_content_dict_and_list() -> None:
    """Test that dicts and lists are serialized to valid JSON."""
    result = {"hits": [1, 2], "ok": True, "q": "café"}
    encoded = _utils.encode_tool_output_content(result)
    assert encoded == '{"hits": [1, 2], "ok": true, "q": "caf\\u00e9"}'

    list_result = ["alpha", "beta"]
    assert _utils.encode_tool_output_content(list_result) == '["alpha", "beta"]'


def test_encode_tool_output_content_primitives() -> None:
    """Test that primitives are serialized to JSON."""
    assert _utils.encode_tool_output_content(42) == "42"
    assert _utils.encode_tool_output_content(3.14) == "3.14"
    assert _utils.encode_tool_output_content(True) == "true"
    assert _utils.encode_tool_output_content(None) == "null"


def test_encode_tool_output_content_models_and_protocols() -> None:
    """Test that Pydantic models and Jsonable objects are serialized to JSON."""
    model = _DummyModel(name="test", count=3)
    assert _utils.encode_tool_output_content(model) == '{"name":"test","count":3}'
    assert _utils.encode_tool_output_content(_DummyJsonable()) == '{"dummy": true}'

    nested = {"model": model}
    assert (
        _utils.encode_tool_output_content(nested)
        == '{"model": {"name": "test", "count": 3}}'
    )


def test_encode_tool_output_content_unserializable_raises() -> None:
    """Test that non-serializable objects raise TypeError."""

    class _Unserializable:
        pass

    with pytest.raises(TypeError, match="is not JSON serializable"):
        _utils.encode_tool_output_content(_Unserializable())


def test_encode_tool_output_response_string() -> None:
    """Test that strings are wrapped under 'output' for Google."""
    assert _utils.encode_tool_output_response("hello") == {"output": "hello"}


def test_encode_tool_output_response_dict() -> None:
    """Test that dicts are passed as structured responses directly for Google."""
    result = {"hits": [1, 2], "ok": True, "q": "café"}
    assert _utils.encode_tool_output_response(result) == {
        "hits": [1, 2],
        "ok": True,
        "q": "café",
    }


def test_encode_tool_output_response_list_and_primitives() -> None:
    """Test that non-mapping values are wrapped under 'output' for Google."""
    assert _utils.encode_tool_output_response(["alpha", "beta"]) == {
        "output": ["alpha", "beta"]
    }
    assert _utils.encode_tool_output_response(42) == {"output": 42}
    assert _utils.encode_tool_output_response(True) == {"output": True}
    assert _utils.encode_tool_output_response(None) == {"output": None}


def test_encode_tool_output_response_models_and_protocols() -> None:
    """Test that Pydantic models and Jsonable objects serializing to dicts are passed directly."""
    model = _DummyModel(name="test", count=3)
    assert _utils.encode_tool_output_response(model) == {"name": "test", "count": 3}
    assert _utils.encode_tool_output_response(_DummyJsonable()) == {"dummy": True}

    nested = {"model": model}
    assert _utils.encode_tool_output_response(nested) == {
        "model": {"name": "test", "count": 3}
    }
