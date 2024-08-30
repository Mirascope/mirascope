"""Get the JSON output from an anthropic call response or chunk."""

import json

from ..call_response import AnthropicCallResponse
from ..call_response_chunk import AnthropicCallResponseChunk


def get_json_output(
    response: AnthropicCallResponse | AnthropicCallResponseChunk, json_mode: bool
) -> str:
    """Get the JSON output from a completion response."""
    if isinstance(response, AnthropicCallResponse):
        if json_mode and (content := response.content):
            json_start = content.index("{")
            json_end = content.rfind("}")
            return content[json_start : json_end + 1]
        for block in response.response.content:
            if block.type == "tool_use" and block.input is not None:
                return json.dumps(block.input)
        raise ValueError("No tool call or JSON object found in response.")
    else:
        if json_mode:
            return response.content
        elif (
            response.chunk.type == "content_block_delta"
            and (delta := response.chunk.delta)
            and delta.type == "input_json_delta"
        ):
            return delta.partial_json
        return ""
