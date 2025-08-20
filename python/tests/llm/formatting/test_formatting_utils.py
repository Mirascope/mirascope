"""Tests for the formatting utils."""

import logging
from typing import cast

import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel

from mirascope import llm
from tests import utils


def test_ensure_formattable_decorates_if_necessary() -> None:
    class Undecorated(BaseModel): ...

    llm.formatting._utils.resolve_formattable(
        Undecorated, model_has_native_json_support=True, model_supports_strict_mode=True
    )
    format = utils.get_format(Undecorated)
    assert format.name == "Undecorated"
    assert format.mode == "strict-or-tool"
    assert (
        cast(llm.formatting.Formattable, Undecorated).__mirascope_format_info__
        == format
    )


def test_ensure_formattable_doesnt_override() -> None:
    @llm.format(mode="json")
    class Decorated(BaseModel): ...

    format = llm.formatting._utils.resolve_formattable(
        Decorated, model_has_native_json_support=True, model_supports_strict_mode=True
    )
    assert format.mode == "json"


def test_ensure_formattable_allows_subsequent_override() -> None:
    class Model(BaseModel): ...

    format = llm.formatting._utils.resolve_formattable(
        Model, model_has_native_json_support=True, model_supports_strict_mode=True
    )
    assert format.info.mode == "strict-or-tool"

    llm.format(Model, mode="json")
    format = llm.formatting._utils.resolve_formattable(
        Model, model_has_native_json_support=True, model_supports_strict_mode=True
    )
    assert format.mode == "json"


def create_format(
    mode: llm.formatting.FormattingMode, instructions: str | None = None
) -> type[BaseModel]:
    @llm.format(mode=mode)
    class Format(BaseModel):
        int_field: int

        @classmethod
        def formatting_instructions(cls) -> str | None:
            return instructions

    return Format


def create_format_no_instructions(
    mode: llm.formatting.FormattingMode,
) -> type[BaseModel]:
    @llm.format(mode=mode)
    class Format(BaseModel):
        int_field: int

    return Format


@pytest.mark.parametrize(
    "mode,model_supports_strict,expected_mode",
    [
        ("strict", True, "strict"),
        ("json", True, "json"),
        ("tool", True, "tool"),
        ("strict-or-tool", True, "strict"),
        ("strict-or-json", True, "strict"),
        ("strict", False, "strict"),
        ("json", False, "json"),
        ("tool", False, "tool"),
        ("strict-or-tool", False, "tool"),
        ("strict-or-json", False, "json"),
    ],
)
def test_mode_resolution(
    mode: llm.formatting.FormattingMode,
    model_supports_strict: bool,
    expected_mode: llm.formatting.ConcreteFormattingMode,
) -> None:
    """Test that modes are resolved correctly based on model capabilities."""

    resolved_info = llm.formatting._utils.resolve_formattable(
        create_format(mode=mode),
        model_supports_strict_mode=model_supports_strict,
        model_has_native_json_support=True,
    )
    assert resolved_info.mode == expected_mode


def test_fallback_logging(caplog: pytest.LogCaptureFixture) -> None:
    """Test that fallback mode changes are logged."""
    with caplog.at_level(logging.DEBUG):
        llm.formatting._utils.resolve_formattable(
            create_format(mode="strict-or-tool"),
            model_supports_strict_mode=False,
            model_has_native_json_support=True,
        )
        assert (
            "Model does not support strict formatting; falling back to tool"
            in caplog.messages
        )

        caplog.clear()
        format_info_json = create_format(mode="strict-or-json")
        llm.formatting._utils.resolve_formattable(
            format_info_json,
            model_supports_strict_mode=False,
            model_has_native_json_support=True,
        )
        assert (
            "Model does not support strict formatting; falling back to json"
            in caplog.messages
        )


@pytest.mark.parametrize(
    "mode", ["strict", "json", "tool", "strict-or-tool", "strict-or-json"]
)
def test_formatting_instructions_preserved(
    mode: llm.formatting.FormattingMode,
) -> None:
    """Test that returning none as formatting instructions disable auto-generation for all modes."""

    resolved_info = llm.formatting._utils.resolve_formattable(
        create_format(mode=mode, instructions=None),
        model_supports_strict_mode=False,
        model_has_native_json_support=False,
    )

    assert resolved_info.formatting_instructions is None


@pytest.mark.parametrize(
    "name,mode,model_has_native_json",
    [
        ("strict-mode", "strict", True),
        ("json-mode-native", "json", True),
        ("json-mode-patched", "json", False),
        ("tool-mode", "tool", True),
    ],
)
def test_auto_generated_formatting_instructions(
    name: str,
    mode: llm.formatting.ConcreteFormattingMode,
    model_has_native_json: bool,
) -> None:
    """Test auto-generated formatting instructions for all concrete mode settings."""

    resolved_info = llm.formatting._utils.resolve_formattable(
        create_format_no_instructions(mode=mode),
        model_supports_strict_mode=True,
        model_has_native_json_support=model_has_native_json,
    )

    assert (
        resolved_info.formatting_instructions
        == snapshot(
            {
                "strict-mode": None,
                "json-mode-native": """\
Respond with valid JSON that matches this exact schema:

```json
{
  "properties": {
    "int_field": {
      "title": "Int Field",
      "type": "integer"
    }
  },
  "required": [
    "int_field"
  ],
  "title": "Format",
  "type": "object"
}
```\
""",
                "json-mode-patched": """\
Respond with valid JSON that matches this exact schema:

```json
{
  "properties": {
    "int_field": {
      "title": "Int Field",
      "type": "integer"
    }
  },
  "required": [
    "int_field"
  ],
  "title": "Format",
  "type": "object"
}
```
Respond ONLY with valid JSON, and no other text.\
""",
                "tool-mode": """\
When you are ready to respond to the user, call the __mirascope_formatted_output_tool__ tool to output a structured response.
Do NOT output any text in addition to the tool call.\
""",
            }
        )[name]
    )


def test_empty_schema_generation() -> None:
    """Test formatting instructions in JSON mode with an empty schema."""

    @llm.format(mode="json")
    class Format(BaseModel): ...

    resolved_info = llm.formatting._utils.resolve_formattable(
        Format,
        model_has_native_json_support=True,
        model_supports_strict_mode=True,
    )

    assert resolved_info.formatting_instructions == snapshot("""\
Respond with valid JSON that matches this exact schema:

```json
{
  "properties": {},
  "title": "Format",
  "type": "object"
}
```\
""")


def test_nested_schema_generation() -> None:
    """Test formatting instructions in JSON mode with a nested schema."""

    class Inner(BaseModel):
        field: str

    @llm.format(mode="json")
    class Format(BaseModel):
        inner: Inner

    resolved_info = llm.formatting._utils.resolve_formattable(
        Format,
        model_has_native_json_support=True,
        model_supports_strict_mode=True,
    )

    assert resolved_info.formatting_instructions == snapshot("""\
Respond with valid JSON that matches this exact schema:

```json
{
  "$defs": {
    "Inner": {
      "properties": {
        "field": {
          "title": "Field",
          "type": "string"
        }
      },
      "required": [
        "field"
      ],
      "title": "Inner",
      "type": "object"
    }
  },
  "properties": {
    "inner": {
      "$ref": "#/$defs/Inner"
    }
  },
  "required": [
    "inner"
  ],
  "title": "Format",
  "type": "object"
}
```\
""")
