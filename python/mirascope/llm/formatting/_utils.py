"""Utilities for the formatting module."""

import inspect
import json

from ..tools import FORMAT_TOOL_NAME
from .types import FormattingMode

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
