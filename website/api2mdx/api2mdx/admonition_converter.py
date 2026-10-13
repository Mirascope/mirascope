"""Utilities for converting MkDocs admonitions to MDX callout components.

This module provides functions to convert MkDocs-style admonitions (!!!note)
to MDX-style callout components (<Note>, <Info>, etc).
"""

import re
from re import Match


def convert_admonitions(content: str) -> str:
    """Convert MkDocs admonitions to MDX callout components.

    Args:
        content: The content to process

    Returns:
        Content with admonitions converted to MDX callouts

    """
    # Handle !!! admonition blocks like:
    # !!! note "Base Class Definition"
    #     This class is simply a means of binding type variables...
    pattern = r"!!! (\w+)(?: \"(.+?)\")??\n([\s\S]+?)(?=\n\n|\Z)"

    def replacement(match: Match) -> str:
        admonition_type = match.group(1).lower()
        title = (
            match.group(2) or None
        )  # Use None to default to component's default title
        content = match.group(3).strip()

        # Map MkDocs admonition types to supported MDX callout types
        # Based on Callout.tsx, we have: note, warning, info, success, api
        type_mapping = {
            "note": "Note",
            "info": "Info",
            "tip": "Info",
            "success": "Success",
            "warning": "Warning",
            "danger": "Warning",
            "error": "Warning",
            "example": "Info",
            "question": "Info",
            "abstract": "Info",
            "quote": "Info",
            "bug": "Warning",
        }

        component_type = type_mapping.get(admonition_type, "Note")

        # Format as MDX callout component
        if title:
            return f'<{component_type} title="{title}">\n\n{content}\n\n</{component_type}>\n\n'
        else:
            return f"<{component_type}>\n\n{content}\n\n</{component_type}>\n\n"

    return re.sub(pattern, replacement, content, flags=re.DOTALL)
