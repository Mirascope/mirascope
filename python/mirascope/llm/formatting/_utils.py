"""Utils associated with formatting."""

import inspect
import json
import logging
from typing import cast

from ..tools import FORMAT_TOOL_NAME
from .decorator import format
from .types import (
    ConcreteFormattingMode,
    FormatInfo,
    FormatT,
    Formattable,
    FormattingMode,
    HasFormattingInstructions,
    ResolvedFormatInfo,
)

TOOL_MODE_INSTRUCTIONS = inspect.cleandoc(f"""
    When you are ready to respond to the user, call the {FORMAT_TOOL_NAME} tool to output a structured response.
    Do NOT output any text in addition to the tool call.
    """)


JSON_MODE_INSTRUCTIONS = (
    "Respond with valid JSON that matches this exact schema:\n{json_schema}"
)


JSON_MODE_FALLBACK_INSTRUCTION = "\nRespond ONLY with valid JSON, and no other text."


def _resolve_concrete_mode(
    mode: FormattingMode,
    *,
    model_supports_strict_mode: bool,
) -> ConcreteFormattingMode:
    """Resolve a formatting mode to a concrete mode based on model capabilities."""
    if not model_supports_strict_mode:
        if mode == "strict-or-tool":
            logging.debug(
                "Model does not support strict formatting; falling back to tool"
            )
            return "tool"
        elif mode == "strict-or-json":
            logging.debug(
                "Model does not support strict formatting; falling back to json"
            )
            return "json"
        # Note: We return "strict" mode as-is, even though it's unsupported, and will
        # let the client raise an appropriate error.
        return mode
    else:
        if mode in ("strict-or-tool", "strict-or-json"):
            return "strict"
        return mode


def _generate_formatting_instructions(
    format_info: FormatInfo,
    *,
    concrete_mode: ConcreteFormattingMode,
    model_has_native_json_support: bool,
) -> str | None:
    """Generate formatting instructions for the given mode and format info."""

    if isinstance(format_info.format, HasFormattingInstructions):
        return format_info.format.formatting_instructions()
    else:
        if concrete_mode == "tool":
            return TOOL_MODE_INSTRUCTIONS
        elif concrete_mode == "json":
            json_schema = json.dumps(format_info.schema, indent=2)
            instructions = JSON_MODE_INSTRUCTIONS.format(json_schema=json_schema)
            if not model_has_native_json_support:
                instructions += "\n" + JSON_MODE_FALLBACK_INSTRUCTION
            return inspect.cleandoc(instructions)


def resolve_formattable(
    formattable: type[FormatT],
    *,
    model_supports_strict_mode: bool,
    model_has_native_json_support: bool,
) -> ResolvedFormatInfo:
    """Resolve a forrmattable into a ResolvedFormatInfo with concrete mode and instructions.

    Note: If the formattable has not been decorated via the format decorator, this method
    will decorate it with default settings.

    Args:
        forrmattable: The FormatT formattable to resolve
        model_supports_strict_mode: Whether the model supports strict structured outputs
        model_has_native_json_support: Whether the model has native JSON mode support

    Returns:
        ResolvedFormatInfo with concrete formatting mode and instructions
    """

    if isinstance(formattable, Formattable):
        format_info = formattable.__mirascope_format_info__
    else:
        format_info = cast(Formattable, format(formattable)).__mirascope_format_info__

    concrete_mode = _resolve_concrete_mode(
        format_info.mode, model_supports_strict_mode=model_supports_strict_mode
    )

    formatting_instructions = _generate_formatting_instructions(
        format_info,
        concrete_mode=concrete_mode,
        model_has_native_json_support=model_has_native_json_support,
    )

    return ResolvedFormatInfo(
        info=format_info,
        mode=concrete_mode,
        formatting_instructions=formatting_instructions,
    )
