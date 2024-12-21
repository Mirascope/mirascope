"""A function generating content to request JSON mode from models without it."""

import json

from pydantic import BaseModel

from ..tool import GenerateJsonSchemaNoTitles


def json_mode_content(tool_type: type[BaseModel] | None) -> str:
    """Returns the content to request JSON mode from models without it."""
    if not tool_type:
        return "\n\nFor your final response, output ONLY a valid JSON dict that adheres to the schema"
    return f"""

For your final response, output ONLY a valid JSON dict (NOT THE SCHEMA) from the content that adheres to this schema:
{json.dumps(tool_type.model_json_schema(schema_generator=GenerateJsonSchemaNoTitles), indent=2)}"""
