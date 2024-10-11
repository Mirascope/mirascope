"""Get the JSON output from a completion response."""

import json

from ..call_response import BedrockCallResponse
from ..call_response_chunk import BedrockCallResponseChunk


def get_json_output(
    response: BedrockCallResponse | BedrockCallResponseChunk, json_mode: bool
) -> str:
    """Get the JSON output from a completion response."""
    if isinstance(response, BedrockCallResponse):
        if json_mode and response.content:
            return response.content
        elif message := response.message:
            tool_calls = [t for c in message["content"] if (t := c.get("toolUse"))]
            if tool_calls and (tool_call_input := tool_calls[0].get("input", {})):
                return json.dumps(tool_call_input)
        raise ValueError("No tool call or JSON object found in response.")
    else:
        if json_mode:
            return response.content
        elif (
            (content_block_delta := response.chunk.get("contentBlockDelta"))
            and (tool_use := content_block_delta["delta"].get("toolUse"))
            and (tool_use_input := tool_use.get("input"))
        ):
            return tool_use_input
    return ""
