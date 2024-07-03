"""Get JSON output from a Gemini response."""

from ..call_response import GeminiCallResponse
from ..call_response_chunk import GeminiCallResponseChunk


def get_json_output(
    response: GeminiCallResponse | GeminiCallResponseChunk, json_mode: bool
) -> str:
    """Extracts the JSON output from a Gemini response."""
    if isinstance(response, GeminiCallResponse):
        if json_mode and response.content:
            return response.content
        elif tool_calls := response.tool_calls:
            return tool_calls[0].function_call.args
        else:
            raise ValueError("No tool call or JSON object found in response.")
    elif not json_mode:
        raise ValueError("Gemini only supports structured streaming in json mode.")
    return response.content
