"""Utility for parsing the content template for a single message parameter."""

from typing import Any

from ..message_param import BaseMessageParam
from .format_template import format_template


def parse_content_template(
    role: str, template: str, attrs: dict[str, Any]
) -> BaseMessageParam | None:
    """Returns the content template parsed and formatted as a message parameter."""
    if not template:
        return None
    content = format_template(template, attrs)
    return BaseMessageParam(role=role, content=content)
