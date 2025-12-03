"""Utilities for the formatting module."""

import inspect
import json
from typing import Any, cast

from ..tools import FORMAT_TOOL_NAME, ToolFn, ToolParameterSchema, ToolSchema
from .types import Format, FormattableT, FormattingMode

TOOL_MODE_INSTRUCTIONS = f"""Always respond to the user's query using the {FORMAT_TOOL_NAME} tool for structured output."""


JSON_MODE_INSTRUCTIONS = (
    "Respond only with valid JSON that matches this exact schema:\n{json_schema}"
)


def default_formatting_instructions(
    schema: dict[str, object], mode: FormattingMode
) -> str | None:
    """Generate formatting instructions for the given mode and format info."""

    if mode == "tool":
        return TOOL_MODE_INSTRUCTIONS
    elif mode == "json":
        json_schema = json.dumps(schema, indent=2)
        instructions = JSON_MODE_INSTRUCTIONS.format(json_schema=json_schema)
        return inspect.cleandoc(instructions)


def create_tool_schema(
    format: Format[FormattableT],
) -> ToolSchema[ToolFn[..., None]]:
    """Convert a `Format` to a `ToolSchema` for format parsing.

    Args:
        format: The `Format` instance containing schema and metadata

    Returns:
        `ToolSchema` for the format tool
    """

    schema_dict: dict[str, Any] = format.schema.copy()
    schema_dict["type"] = "object"

    properties = schema_dict.get("properties")
    if not properties or not isinstance(properties, dict):
        properties = {}  # pragma: no cover
    properties = cast(dict[str, Any], properties)
    required: list[str] = list(properties.keys())

    description = (
        f"Use this tool to extract data in {format.name} format for a final response."
    )
    if format.description:
        description += "\n" + format.description

    parameters = ToolParameterSchema(
        properties=properties,
        required=required,
        additionalProperties=False,
    )
    if "$defs" in schema_dict and isinstance(schema_dict["$defs"], dict):
        parameters.defs = schema_dict["$defs"]

    def _unused_format_fn() -> None:
        raise TypeError(
            "Format tool function should not be called."
        )  # pragma: no cover

    tool_schema = cast(ToolSchema[ToolFn[..., None]], ToolSchema.__new__(ToolSchema))
    tool_schema.fn = _unused_format_fn
    tool_schema.name = FORMAT_TOOL_NAME
    tool_schema.description = description
    tool_schema.parameters = parameters
    tool_schema.strict = True

    return tool_schema
