from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    ToolCall,
    ToolOutput,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic-beta/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {"thinking": {"level": "none"}},
            "finish_reason": None,
            "usage": {
                "input_tokens": 477,
                "output_tokens": 26,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "BetaUsage(cache_creation=BetaCacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=477, output_tokens=26, server_tool_use=None, service_tier='standard')",
                "total_tokens": 503,
            },
            "messages": [
                UserMessage(content=[Text(text="What is the 100th fibonacci number?")]),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="compute_fib",
                            args='{"n": 100}',
                        )
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
                                "thought_signature": b'\n\xe2\x01\x01r\xc8\xda|\x13\x0e\xf0\x8f\xf7X\xf0\xc9\x06\x0c\x11[f\xb8IW\x02\x86\xa4\xf3m\x8d\xa8\xaf\xaaeN\xa5\xa8\xcc+\xf8\x8fO\xcb\xa0;E\xacsd@\x80[,\xe8?NY\xe7\xac\xe6\x1e\x87l\xc25\x0cTq:\xa1\xdc5\xef\x9a\xcd\xb2\xde\x82\xdb/"\xf2\x8e\xdb\xf7\x12\x8c\x88\xd3g;K\x9bjKrp\xdc\xa5\xcf\xfc\xd5^\xa5\x94k\xb9`\x91q\x00S\x05hqW\x05\xf2\xa5\x85-4\x85\xf9\xe1\r\x85&Lh!\xe7 \x8b\xcc\xde\xef\xfa\x0c\x93\x8f\x94-\xbc\x1d\xa4\x9d\xbd\xe9\x84j1\xcb\xd3\x9a\xae#\x9b\x1b\xde\xf7\xaa5\xd9\xcd\x8e\x17\xe3\xa6<]\x06\xc5,\xe7\xbe\x0c5\x13&"\xafC\xe3\xbf\xaf\xc3\xbfcyE\x84\xb24\xa9\x0b\xc8\xf6~1\xde\x84\x13\x17\x8e\xae\xfd&]\xb3\xa1\xb6\x0f%=\x00\x9f\xc06\x9a\xc1\x0c\xb7\xa0A)\x83?I',
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="google_unknown_tool_id",
                            name="compute_fib",
                            result="218922995834555169026",
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
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
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
                    "strict": None,
                }
            ],
        }
    }
)
