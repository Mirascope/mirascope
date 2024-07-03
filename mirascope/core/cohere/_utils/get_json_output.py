"""Get the JSON output from a completion response."""

import json

from ..call_response import CohereCallResponse
from ..call_response_chunk import CohereCallResponseChunk


def get_json_output(
    response: CohereCallResponse | CohereCallResponseChunk, json_mode: bool
) -> str:
    """Get the JSON output from a completion response."""
    if isinstance(response, CohereCallResponse):
        if json_mode and response.content:
            return response.content
        elif response.tool_calls:
            return json.dumps(response.tool_calls[0].parameters)
        raise ValueError("No tool call or JSON object found in response.")
    else:
        # raise ValueError("Cohere does not support structured streaming... :(")
        if json_mode:
            return response.content
        elif (tool_calls := response.tool_calls) and (
            parameters := tool_calls[0].parameters
        ):
            return json.dumps(parameters)
        return ""
