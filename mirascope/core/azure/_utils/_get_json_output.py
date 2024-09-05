"""Get the JSON output from a completion response."""

from ..call_response import AzureCallResponse
from ..call_response_chunk import AzureCallResponseChunk


def get_json_output(
    response: AzureCallResponse | AzureCallResponseChunk, json_mode: bool
) -> str:
    """Get the JSON output from a completion response."""
    if isinstance(response, AzureCallResponse):
        if json_mode and response.content:
            return response.content
        elif tool_calls := response.response.choices[0].message.tool_calls:
            return tool_calls[0].function.arguments
        raise ValueError("No tool call or JSON object found in response.")
    else:
        if json_mode:
            return response.content
        elif (
            (choices := response.chunk.choices)
            and (tool_calls := choices[0].delta.tool_calls)
            and (function := tool_calls[0].function)
            and (arguments := function.arguments) is not None
        ):
            return arguments
        return ""
