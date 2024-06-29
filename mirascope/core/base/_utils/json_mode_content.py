"""A function generating content to request JSON mode from models without it."""

import json
from textwrap import dedent

from ..tool import BaseTool


def json_mode_content(tool_type: type[BaseTool] | None):
    """Returns the content to request JSON mode from models without it."""
    if not tool_type:
        return "\n\nExtract ONLY a valid JSON dict using the schema."
    return dedent(f"""
                  
    Extract ONLY a valid JSON dict from the content using this schema:
    {json.dumps(tool_type.model_json_schema(), indent=2)}""")
