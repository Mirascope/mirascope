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
                                "thought_signature": b'\n\xeb\x01\x01r\xc8\xda|\x80!\x17\x89\xbbR96J\x8eO\xe5\xf3N\x885r\r2\xe4g\xa8\x83b\xb9c\xc7\xda\xb7\xc0-\x91C\x94?\xa0<\xb8Ol\xf1OM\xfe\xe2\x02\x9f7GQ\xdfX\x1a\xf4x\x83\xea\x96dC,\x1dO\x98\xa1\x0f\x9b\xcf\x06#\xb7\x92\x08-\x92\xff\x88%8\xa4\x16\xe4\xf3\x98\xacj\x87\x14\xd7\x9d\n2\xfc<k\x90\x02v\x95\xe1\x8ebt4\x01.\xfa\xd3*\x86\xef\x1d"\x92x\xe00\x908\xce\xdf\\y/\xf3E\x9c\x14vy+\xc2\xd1^\x9bR\xed\xf2\x1e\xef8\xa5]U\xf4mK\x7f\xc4\xa0\x10\x8a\x8b\xdd<\x974\xfd\xf4\xa5\xae\xde{\x14\xf2*\xe7p)\x98\xc7\xf0\xda\x98Sti\x1a\x90\xa7\xaa\xa2\xcfHY|s\r\xc2V\xd8\xb1\x02=O*\x7f\xf5\xbf\xa3\x14\xb8t\xafa\x17\x13\x1d\x04\x90\x82\xc1A\x04\x9b\x83\t\x96=\xe0/8\x12\x9bhW4\xa2\xf3&',
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
                    "strict": False,
                }
            ],
        }
    }
)
