"""Utilities for response classes."""

import json
from typing import cast

import jiter
from pydantic import BaseModel

from ..formatting import (
    FormattableT,
    Partial,
    PrimitiveWrapperModel,
    create_wrapper_model,
    is_primitive_type,
)


def _strip_json_preamble(text: str) -> str | None:
    """Strip preamble text before JSON content.

    Handles cases where models output text before JSON like:
    "Sure thing! Here's the JSON:\n{..."

    Or cases where the model wraps the JSON in code blocks like:
    "```json\n{..."

    Args:
        text: The raw text that may contain a JSON object

    Returns:
        Text starting from the opening `{`, or None if no `{` found.
    """
    code_block_start_marker = "```json"
    code_block_start = text.find(code_block_start_marker)
    if code_block_start > -1:
        # Discard text prior to code block; it takes precedence over brackets that
        # may be found before it.
        text = text[code_block_start:]

    json_start = text.find("{")
    if json_start == -1:
        return None

    return text[json_start:]


def extract_serialized_json(text: str) -> str:
    """Extract the serialized JSON string from text that may contain extra content.

    Handles cases where models output text before JSON like:
    "Sure thing! Here's the JSON:\n{...}"

    Or cases where the model wraps the JSON in code blocks like:
    "```json\n{...}\n```"

    Args:
        text: The raw text that may contain a JSON object

    Raises:
        json.JSONDecodeError: If no valid JSON object could be extracted.

    Returns:
        The extracted serialized JSON string
    """
    stripped = _strip_json_preamble(text)
    if stripped is None:
        raise json.JSONDecodeError("No JSON object found: missing '{'", text, 0)

    # Find the matching closing brace
    brace_count = 0
    in_string = False
    escaped = False

    for i, char in enumerate(stripped):
        if escaped:
            escaped = False
            continue

        if char == "\\":
            escaped = True
            continue

        if char == '"' and not escaped:
            in_string = not in_string
            continue

        if not in_string:
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count == 0:
                    return stripped[: i + 1]

    raise json.JSONDecodeError("No JSON object found: missing '}'", text, len(text))


def parse_partial_json(
    json_text: str, formattable: type[FormattableT]
) -> FormattableT | Partial[FormattableT] | None:
    """Parse incomplete JSON into a Partial model for structured streaming.

    Uses jiter's partial mode to handle incomplete JSON gracefully.
    Returns None if JSON cannot be parsed yet.

    Handles cases where models output text before JSON like:
    "Sure thing! Here's the JSON:\n{..."

    Args:
        json_text: The incomplete JSON string to parse
        formattable: The target format type (BaseModel or PrimitiveType)

    Returns:
        Parsed partial object, or None if unparsable

    Example:
        >>> from pydantic import BaseModel
        >>> class Book(BaseModel):
        ...     title: str
        ...     author: str
        >>> parse_partial_json('{"title": "The Name"', Book)
        PartialBook(title='The Name', author=None)
    """
    # Strip preamble text before JSON
    stripped = _strip_json_preamble(json_text)
    if stripped is None:
        return None

    try:
        parsed = jiter.from_json(stripped.encode(), partial_mode="trailing-strings")
    except Exception:
        return None

    target_model = formattable
    if is_primitive_type(target_model):
        target_model = cast(BaseModel, create_wrapper_model(target_model))

    try:
        instance = cast(BaseModel, Partial[target_model]).model_validate(parsed)
    except Exception:
        return None

    if is_primitive_type(formattable):
        return cast(PrimitiveWrapperModel, instance).output

    return cast(Partial[FormattableT], instance)
