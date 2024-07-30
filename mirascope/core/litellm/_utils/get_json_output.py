"""Get the JSON output from a completion response."""

from typing import cast

from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_chunk import Choice as ChunkChoice

from ..call_response import LiteLLMCallResponse
from ..call_response_chunk import LiteLLMCallResponseChunk


def get_json_output(
    response: LiteLLMCallResponse | LiteLLMCallResponseChunk, json_mode: bool
) -> str:
    """Get the JSON output from a completion response."""
    if isinstance(response, LiteLLMCallResponse):
        if json_mode and response.content:
            return response.content
        elif tool_calls := cast(list[Choice], response.response.choices)[
            0
        ].message.tool_calls:
            return tool_calls[0].function.arguments
        raise ValueError("No tool call or JSON object found in response.")
    else:
        if json_mode:
            return response.content
        elif (
            (choices := response.chunk.choices)
            and (tool_calls := cast(list[ChunkChoice], choices)[0].delta.tool_calls)
            and (function := tool_calls[0].function)
            and (arguments := function.arguments) is not None
        ):
            return arguments
        return ""
