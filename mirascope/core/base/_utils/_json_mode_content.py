"""A function generating content to request JSON mode from models without it."""

import json

from ..tool import BaseTool, GenerateJsonSchemaNoTitles


def json_mode_content(tool_type: type[BaseTool] | None) -> str:
    """Returns the content to request JSON mode from models without it."""
    if not tool_type:
        return "\n\nExtract ONLY a valid JSON dict using the schema."
    return f"""

Extract ONLY a valid JSON dict (NOT THE SCHEMA) from the content that adheres to this schema:
{json.dumps(tool_type.model_json_schema(schema_generator=GenerateJsonSchemaNoTitles), indent=2)}"""
