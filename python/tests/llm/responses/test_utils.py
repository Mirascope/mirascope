import inspect

import pytest

from mirascope.llm.responses._utils import extract_serialized_json


def test_extract_json_from_code_block() -> None:
    text = inspect.cleandoc("""
        ```json
        {"key": "value"}
        ```
    """)
    result = extract_serialized_json(text)
    assert result == '{"key": "value"}'


def test_extract_json_from_code_block_json_contains_code_block() -> None:
    text = inspect.cleandoc("""
        ```json
        {"key": "value": "```json\n{"is_cursed_object": true}\n```"}
        ```
    """)
    result = extract_serialized_json(text)
    assert result == '{"key": "value": "```json\n{"is_cursed_object": true}\n```"}'


def test_extract_json_from_code_block_with_escaped_quotes() -> None:
    text = inspect.cleandoc("""
        ```json
        {"message": "He said \"hello\" and she replied \"```json\n{\"nested\": true}\n```\""}
        ```
    """)
    result = extract_serialized_json(text)
    assert (
        result
        == '{"message": "He said "hello" and she replied "```json\n{"nested": true}\n```""}'
    )


def test_extract_json_from_code_block_with_prefix_text() -> None:
    text = inspect.cleandoc("""
        Sure thing! Here's the JSON:
        ```json
        {"key": "value"}
        ```
    """)
    result = extract_serialized_json(text)
    assert result == '{"key": "value"}'


def test_extract_json_from_multiple_code_blocks() -> None:
    text = inspect.cleandoc("""
        Sure thing! Here's the JSON:
        ```json
        {"key": "value"}
        ```

        Here's some more!!!
        ```json
        {"key2": "value2"}
        ```
    """)
    result = extract_serialized_json(text)
    assert result == '{"key": "value"}'


def test_code_block_takes_precedence_over_bare_json() -> None:
    text = inspect.cleandoc("""
        Sure thing! I'll use that {} (json) notation you mentioned:
        ```json
        {"key": "value"}
        ```
    """)
    result = extract_serialized_json(text)
    assert result == '{"key": "value"}'


def test_extract_json_from_bare_json() -> None:
    text = '{"key": "value"}'
    result = extract_serialized_json(text)
    assert result == '{"key": "value"}'


def test_extract_json_from_bare_json_with_prefix_and_suffix() -> None:
    text = inspect.cleandoc("""
        The result is: {"key": "value"} and that's final
    """)
    result = extract_serialized_json(text)
    assert result == '{"key": "value"}'


def test_extract_nested_json() -> None:
    text = '{"outer": {"inner": {"key": "value"}}}'
    result = extract_serialized_json(text)
    assert result == '{"outer": {"inner": {"key": "value"}}}'


def test_unfinished_json_code_block() -> None:
    text = inspect.cleandoc("""
        ```json
        {"key": "value"}
    """)
    result = extract_serialized_json(text)
    assert result == '{"key": "value"}'


def test_no_opening_brace_raises_error() -> None:
    text = inspect.cleandoc("""
        This has no JSON
    """)
    with pytest.raises(ValueError, match="no opening `{`"):
        extract_serialized_json(text)


def test_no_closing_brace_raises_error() -> None:
    text = inspect.cleandoc("""
        {"key": "value"
    """)
    with pytest.raises(ValueError, match="no closing `}`"):
        extract_serialized_json(text)


def test_empty_string_raises_error() -> None:
    text = ""
    with pytest.raises(ValueError, match="no opening `{`"):
        extract_serialized_json(text)


def test_only_braces_returns_empty_object() -> None:
    text = "{}"
    result = extract_serialized_json(text)
    assert result == "{}"


def test_multiple_json_objects_returns_first_to_last() -> None:
    text = '{"first": "object"} some text {"second": "object"}'
    result = extract_serialized_json(text)
    assert result == '{"first": "object"}'


def test_json_with_newlines_and_formatting() -> None:
    text = inspect.cleandoc("""Here's the formatted JSON:
    {
        "key": "value",
        "nested": {
            "inner": "data"
        }
    }
    That's the result.""")
    result = extract_serialized_json(text)
    expected = inspect.cleandoc("""{
        "key": "value",
        "nested": {
            "inner": "data"
        }
    }""")
    assert result == expected


def test_json_code_block_with_multiple_backticks() -> None:
    text = 'Some text ```json\n{"key": "value"}\n``` more text ```\nother content\n```'
    result = extract_serialized_json(text)
    assert result == '{"key": "value"}'


def test_json_with_escaped_braces_in_string() -> None:
    text = '{"message": "This has \\{ and \\} in it"}'
    result = extract_serialized_json(text)
    assert result == '{"message": "This has \\{ and \\} in it"}'


def test_json_with_json_in_string() -> None:
    text = '{"message": "This has {"nested": true} in it"}'
    result = extract_serialized_json(text)
    assert result == '{"message": "This has {"nested": true} in it"}'
