from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    Thought,
    ToolCall,
    ToolOutput,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {"thinking": {"level": "none"}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 477,
                "output_tokens": 26,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=477, output_tokens=26, server_tool_use=None, service_tier='standard')",
                "total_tokens": 503,
            },
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        Thought(
                            thought="""\
Here's a summary of my thought process:

**Calculating the 100th Fibonacci Number**

Okay, the user wants the 100th Fibonacci number. That's straightforward. I know there's a function available, `default_api.compute_fib`, that's specifically designed for this purpose. The input argument is the `n` for the nth Fibonacci number we want. So, all I need to do is call `default_api.compute_fib` and set `n` to 100. Should be quick and simple.
"""
                        ),
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="compute_fib",
                            args='{"n": 100}',
                        ),
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
Here's a summary of my thought process:

**Calculating the 100th Fibonacci Number**

Okay, the user wants the 100th Fibonacci number. That's straightforward. I know there's a function available, `default_api.compute_fib`, that's specifically designed for this purpose. The input argument is the `n` for the nth Fibonacci number we want. So, all I need to do is call `default_api.compute_fib` and set `n` to 100. Should be quick and simple.
""",
                                "thought": True,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": {
                                    "id": None,
                                    "args": {"n": 100},
                                    "name": "compute_fib",
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b'\n\xe2\x01\x01r\xc8\xda|\xda\xe5\xda\x0c\x1e\xc5t9\xf7\x94S\xc02\x04\xb6{\r\xf4\xbcIw\xad\xf2\x8f\xa4\xd2%\x95\x7f\xee\x10#|\x138\xf0\x8c4!\x95\x94\xffaaNT\xcf\x9a\xa7\xe1\xaeA\x94\xe5\xc2\x8e\xc2/\xd0p8\x17\x0f\x13Ml\x1f\xabYOv\xa0j\xf3r\x88WN2\x8f\xd2$\xf0\xf2Z\xeb\xcb9\x7f\x0f\x1b\xd9\xd9\x9b\x85\xf5"\xe8\xd0\xa8{\xc7Y\xdb\xc4\xb0?\xcd\r\x88\x91\xc9=,\xcb\x88\x16\x1a\xa8J\xe8\x8c\xd1{\x18L\xdd\xb6\xc9\x1eD\xce\x85\xeaM\xf1\x1e\t\xe2\xfb5\xa1\xb7\xbd\xa2\x02N\x00\xf74vHi\xbd\xd2\x81?<\xea\x04< \xc7\x05L"\x8b\xa2R\xa9\xd1\x86\xb2\xc2\xf6\x89D\'\xae\xf8*\x1e\xc4\xda\xa5\xe8\xa1\x8e\xd6jEd\xf7\xd3\xb7 \xd6\x1b+\x19\r\xd0\xceS\xe7\xa4f_k\x1bCx\xa9\x16\t(_\xb6\xd0\xce\x8d',
                                "video_metadata": None,
                            },
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="google_unknown_tool_id",
                            name="compute_fib",
                            value="218922995834555169026",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="The 100th Fibonacci number is 218,922,995,834,555,169,026."
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": "The 100th Fibonacci number is 218,922,995,834,555,169,026.",
                                "type": "text",
                            }
                        ],
                    },
                ),
            ],
            "format": None,
            "tools": [
                {
                    "name": "compute_fib",
                    "description": "Compute the nth Fibonacci number (1-indexed).",
                    "parameters": """\
{
  "properties": {
    "n": {
      "title": "N",
      "type": "integer"
    }
  },
  "required": [
    "n"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": False,
                }
            ],
        }
    }
)
